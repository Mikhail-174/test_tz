from django.core.paginator import Paginator
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import WorkerSerializerRead, WorkerSerializerWrite
from .models import Worker, Position
from .filters import WorkerFilter
from .paginations import CustomPagination
from .permissions import IsAdmin, IsUser
from django.core.exceptions import ObjectDoesNotExist


class WorkerView(APIView):
    """
    View to list and filter list Workers in the DB
    Required User permission
    """
    serializer_class = WorkerSerializerWrite
    serializer_class_read = WorkerSerializerRead

    pagination_class = CustomPagination
    # permission_classes = [IsUser, IsAdmin]

    def get(self, request):
        workers = Worker.objects.all()
        filterset = WorkerFilter(request.query_params, queryset=workers)
        if filterset.is_valid():
            queryset = filterset.qs
            paginator = self.pagination_class()
            paginated_qs = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class_read(paginated_qs, many=True)
            return paginator.get_paginated_response(data=serializer.data)
        else:
            Response(data=filterset.errors, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        # user = request.data['user']
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response({"message": f"Data is not valid! {serializer.errors}"}, status=400)
        data = serializer.validated_data
        first_name = data['first_name']
        middle_name = data['middle_name']
        last_name = data['last_name']
        email = data['email']
        position_str = data['position']['name']
        position, _ = Position.objects.get_or_create(name=position_str)
        # created_by = user

        worker, created = Worker.objects.get_or_create(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            position=position,
            # created_by=user,
        )
        return Response({"message": "Worker created successful!"}, status=200)



class WorkerIDView(APIView):
    """Detail / Update / Delete worker"""

    serializer_class = WorkerSerializerWrite
    serializer_class_read = WorkerSerializerRead

    def get_object(self, id):
        worker_uuid = id
        try:
            worker = Worker.objects.get(id=worker_uuid)
        except ObjectDoesNotExist:
            return None
        else:
            return worker

    def get(self, request, **kwargs):
        worker = self.get_object(id=kwargs['id'])
        if worker is None:
            return Response(data={"message": f"Worker with id {kwargs['id']} does not exist!"}, status=404)
        serializer = self.serializer_class_read(worker)
        return Response(data=serializer.data, status=200)

    def patch(self, request, **kwargs):
        worker = self.get_object(id=kwargs['id'])
        if worker is None:
            return Response(data={"message": f"Worker with id {kwargs['id']} does not exist!"}, status=404)
        serializer = self.serializer_class(worker, request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(data=serializer.errors, status=400)
        serializer.save()
        return Response(data=serializer.data, status=204)

    def delete(self, request, **kwargs):
        worker = self.get_object(id=kwargs['id'])
        if worker is None:
            return Response(data={"message": f"Worker with id {kwargs['id']} does not exist!"}, status=404)
        worker.delete()
        return Response(data={"message": f"Worker with id = {kwargs['id']} deleted successfully!"}, status=200)
