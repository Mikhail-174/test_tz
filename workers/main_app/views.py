from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
from django_filters import rest_framework as filters

from datetime import datetime

from .serializers import WorkerSerializerRead, WorkerSerializerWrite, ExcelFileSerializer, WorkerImportWriteSerializer
from .models import Position, Worker
from .filters import WorkerFilter
from .paginations import CustomPagination
from .permissions import IsAdminOrReadOnly




class WorkerView(APIView):
    """
    View to list and filter list Workers in the DB
    Required User permission
    """
    serializer_class = WorkerSerializerWrite
    serializer_class_read = WorkerSerializerRead

    pagination_class = CustomPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = WorkerFilter

    def get(self, request):
        workers = Worker.objects.all()
        filterset = self.filterset_class(request.query_params, queryset=workers)
        if filterset.is_valid():
            queryset = filterset.qs
            paginator = self.pagination_class()
            paginated_qs = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class_read(paginated_qs, many=True)
            return paginator.get_paginated_response(data=serializer.data)
        else:
            Response(data=filterset.errors, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response({"message": f"Data is not valid! {serializer.errors}"}, status=400)
        data = serializer.validated_data
        first_name = data['first_name']
        middle_name = data.get('middle_name', '')
        last_name = data['last_name']
        email = data['email']
        position_str = data['position']['name']
        position, _ = Position.objects.get_or_create(name=position_str)


        worker, created = Worker.objects.get_or_create(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            position=position,
            created_by=user,
        )
        return Response({"message": "Worker created successful!"}, status=200)



class WorkerIDView(APIView):
    """Detail / Update / Delete worker
    Required User permission on patch and delete methods"""

    serializer_class = WorkerSerializerWrite
    permission_classes = [IsAdminOrReadOnly]

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
        serializer = self.serializer_class(worker)
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
        return Response(data=serializer.validated_data, status=200)

    def delete(self, request, **kwargs):
        worker = self.get_object(id=kwargs['id'])
        if worker is None:
            return Response(data={"message": f"Worker with id {kwargs['id']} does not exist!"}, status=404)
        Worker.objects.get(id=kwargs['id']).delete()
        return Response(data={"message": f"Worker with id = {kwargs['id']} deleted successfully!"}, status=200)

class WorkerImportView(APIView):
    """View for creating objects from imported Excel files"""
    serializer_class = ExcelFileSerializer
    serializer_class_write = WorkerImportWriteSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]  # Важно для загрузки файлов!

    def parse_excel_to_dict_list(self, file):
        dataframe = pd.read_excel(file)
        dict_list = dataframe.to_dict(orient='records')
        return dict_list

    def serializer_error_parser(self, error_dict):
        error_log_string = ""
        for error_reason, value_list in error_dict.items():
            error_log_string += f"{error_reason}:\n"
            for value in value_list:
                error_log_string += f"\t{value}\n"
        return error_log_string


    def post(self, request):
        user = request.user
        file_serializer = self.serializer_class(data=request.data)
        if file_serializer.is_valid():
            serializer_file_data = file_serializer.validated_data
            file_name = serializer_file_data['file']
            new_workers = self.parse_excel_to_dict_list(file_name)
            error_records = list()
            new_workers_count = len(new_workers)
            for record in new_workers:
                try:
                    hired_date = datetime.fromtimestamp(record['hired_date'].timestamp())
                    record['hired_date'] = hired_date
                    if record.get('position', None) is None:
                        record['position'] = "No position"
                    serializer = self.serializer_class_write(data=record)
                    if serializer.is_valid():
                        data = serializer.validated_data
                        position, _ = Position.objects.get_or_create(name=record['position'])
                        new_worker = Worker(
                            first_name=data['first_name'],
                            middle_name=data.get('middle_name', ''),
                            last_name=data['last_name'],
                            email=data['email'],
                            position=position,
                            hired_date=data.get("hired_date", None),
                            created_by=user,
                        )
                        new_worker.save()
                    else:
                        error_records.append(self.serializer_error_parser(serializer.errors))
                except Exception as error:
                    error_records.append(self.serializer_error_parser(serializer.errors))

            print(*error_records, sep='\n')
            print(f"New workers count: {new_workers_count - len(error_records)}")
            if new_workers_count == len(error_records):
                return Response(data={"message": "Unsuccess file reading"}, status=400)
            return Response(data={"message": "success file uploaded"}, status=200)
        else:
            return Response(data=file_serializer.errors, status=400)
