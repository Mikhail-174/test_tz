from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from .models import Worker, Position
from .views import WorkerView, WorkerIDView, WorkerImportView
from .serializers import WorkerSerializerWrite, WorkerSerializerRead, WorkerImportWriteSerializer
from .paginations import CustomPagination

import requests
import os
import random
import math
import json
import uuid
from pathlib import Path

namespaces = ("workers", "worker_RUD", "excel_import")
position_names = ("Senior Developer", "Project Manager", "DevOps Engineer", "UX/UI Designer", "Data Scientist", "QA Engineer", "Team Lead", "Frontend Developer", "Backend Developer", "HR Manager", "Mobile Developer", "Product Manager", "System Administrator", "Marketing Specialist", "Security Engineer", "Business Analyst", "Database Administrator")

class WorkerTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.count_of_records = 50
        for position in position_names:
            Position.objects.create(name=position)
        self.positions = Position.objects.all()
        self.the_fake = Faker(['ru_RU'])

        for i in range(self.count_of_records):
            pos = random.choice(self.positions)
            Worker.objects.create(  first_name=self.the_fake.first_name(), last_name=self.the_fake.last_name(),            email=self.the_fake.email(), position=pos)

    def user_admin_producer(self):
        creep_user = get_user_model().objects.create(
            username="test_user",
            password="testpassword1234")
        admin_user = get_user_model().objects.create(
            username="test_admin",
            password="testpassword1234")
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        all_perms = Permission.objects.all()
        for perm in all_perms:
            if "main_app" in perm.natural_key() and "worker" in perm.natural_key():
                admin_group.permissions.add(perm)
            if "main_app" in perm.natural_key() and "position" in perm.natural_key():
                admin_group.permissions.add(perm)
        admin_user.groups.add(admin_group)
        return creep_user, admin_user

    def test_get_workers_view_paginate(self):
        """Test WorkerView with no parameters
        checking all pages status code
        checking record counts """

        serializer_class = WorkerSerializerRead
        url = reverse(namespaces[0])
        data = {}
        # view = WorkerView.as_view({'get': 'get'})
        view = WorkerView.as_view()
        next_page = ""
        page_count = 0
        unique_id_error_count = 0
        while next_page is not None:
            page_count += 1
            request = self.factory.get(url, data, format='json')
            response = view(request)
            url = response.data['next']
            next_page = url
            serializer = serializer_class(data=response.data['results'], many=True)
            serializer.is_valid()
            for error in serializer.errors:
                if error['id'][0].code == 'unique':
                    unique_id_error_count += 1

            self.assertEqual(response.status_code, 200)
        self.assertEqual(page_count, math.ceil(self.count_of_records / CustomPagination.page_size))
        self.assertEqual(unique_id_error_count, self.count_of_records)
        self.assertEqual(response.data['count'], self.count_of_records)

    def test_get_workers_view_filters_developer(self):
        """Test WorkerView with filters
            checking all pages status code
            checking record counts by filter option developer"""
        url = reverse(namespaces[0])
        view = WorkerView.as_view()
        pos_names_count_dict = dict()
        for pn in position_names:
            pos_names_count_dict[pn] = Worker.objects.filter(position__name__icontains=pn).count()
        for pn in position_names:
            filter = f"?position={pn}"
            filt_url = url + filter
            request = self.factory.get(filt_url, format='json')
            response = view(request)
            self.assertEqual(response.data['count'], pos_names_count_dict[pn])
            self.assertEqual(response.status_code, 200)


    def test_get_workers_view_filters_is_active(self):
        """Test WorkerView with filters
            checking all pages status code
            checking record counts by filter option developer and is_active"""
        url = reverse(namespaces[0])
        view = WorkerView.as_view()
        pos_names_is_acitve_count_dict = {pos: dict() for
        pos in position_names}
        for pn in position_names:
            pos_names_is_acitve_count_dict[pn][1] = Worker.objects.filter(position__name__icontains=pn, is_active=True).count()
            pos_names_is_acitve_count_dict[pn][0] = Worker.objects.filter(position__name__icontains=pn, is_active=False).count()

        for pn in position_names:
            for i in range(2):
                filter = f"?position={pn}&is_active={bool(i)}"
                filt_url = url + filter
                request = self.factory.get(filt_url, format='json')
                response = view(request)
                self.assertEqual(response.data['count'], pos_names_is_acitve_count_dict[pn][i])
                self.assertEqual(response.status_code, 200)

    def test_post_worker_view_user(self):
        """Test WorkerView with POST mehtod
            user with no permissions can't create Workers
            user with Admin group - can"""
        url = reverse(namespaces[0])
        creep_user, admin_user = self.user_admin_producer()
        self.client.force_authenticate(user=creep_user)
        data = {
          "position": {
            "name": f"{random.choice(self.positions)}"},
          "first_name": self.the_fake.first_name(),
          "last_name": self.the_fake.last_name(),
          "email": self.the_fake.email(),}
        response = self.client.post(path=url, data=data, format="json")
        self.assertIn(response.status_code, (403,))

        # reset user
        self.client.force_authenticate(user=None)

        self.client.force_authenticate(user=admin_user)
        response = self.client.post(path=url, data=data, format='json')
        self.assertIn(response.status_code, (200,))

    def test_RUD_worker_id_view_user(self):
        """Test WorkerIDView with RUD mehtods
            user with no permissions can't update/delete Workers
            user with Admin group - can"""
        view = WorkerIDView.as_view()
        creep_user, admin_user = self.user_admin_producer()
        self.client.force_authenticate(user=creep_user)
        for worker in Worker.objects.all():
            user_uuid = worker.id
            wrong_uuid = uuid.uuid4()
            while wrong_uuid == user_uuid:
                wrong_uuid = uuid.uuid4()
            url = reverse(namespaces[1], args=(user_uuid,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            response = self.client.patch(url)
            self.assertEqual(response.status_code, 403)
            response = self.client.delete(url)
            self.assertEqual(response.status_code, 403)

            url = reverse(namespaces[1], args=(wrong_uuid,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

        self.client.force_authenticate(user=None)
        self.client.force_authenticate(user=admin_user)

        for worker in Worker.objects.all():
            user_uuid = worker.id
            while wrong_uuid == user_uuid:
                wrong_uuid = uuid.uuid4()
            url = reverse(namespaces[1], args=(user_uuid,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            changed_position = Position.objects.get(id=1)
            data = {
                "id": worker.id,
                "position": {
                    "id": changed_position.id,
                    "name": changed_position.name
                },
                "first_name": "new_" + worker.first_name,
                "middle_name": worker.middle_name,
                "last_name": worker.last_name,
                "email": worker.email,
                "is_active": True,
                "hired_date": "2025-10-24T00:00:00Z",
                "is_deleted": False,
                "deleted_at": None,
            }
            response = self.client.patch(url, data=data, format="json")
            worker = Worker.objects.get(id=user_uuid)
            self.assertEqual(response.status_code, 204)
            self.assertEqual(worker.first_name.startswith("new_"), True)

            response = self.client.delete(url)
            deleted_worker = Worker.objects.unfiltered().get(id=user_uuid)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(deleted_worker.is_deleted, True)

            url = reverse(namespaces[1], args=(wrong_uuid,))
            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, 404)
            response = self.client.patch(url, format="json")
            self.assertEqual(response.status_code, 404)
            response = self.client.delete(url, format="json")
            self.assertEqual(response.status_code, 404)

    def test_import_excel(self):
        """Test WorkerImportView
            import excel-file doesn't be processing
            if user has no Admin permissions
            user with Admin group - can"""
        view = WorkerImportView
        url = reverse(namespaces[2])
        creep_user, admin_user = self.user_admin_producer()
        test_imports_path = Path(__file__).resolve().parent.parent / 'test_imports'
        path_files = os.listdir(path=test_imports_path)

        self.client.force_authenticate(user=creep_user)
        for file in path_files:
            if file.endswith(".xlsx"):
                file_path = test_imports_path / file
                excel_file_data = {'file': open(file_path, 'rb')}
                response = self.client.post(url, data=excel_file_data)

                self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(user=None)
        self.client.force_authenticate(user=admin_user)
        for file in path_files:
            if file.endswith(".xlsx"):
                file_path = test_imports_path / file
                excel_file_data = {'file': open(file_path, 'rb')}
                print("-" * 80)
                response = self.client.post(url, data=excel_file_data)
                print("-" * 80)
                self.assertEqual(response.status_code, 200)