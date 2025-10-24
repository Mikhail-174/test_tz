from django.shortcuts import render
from rest_framework.views import APIView

from serializers import WorkerSerializer
from models import Worker
from filters import WorkerFilter
from paginations import CustomPagination
from permissions import IsAdmin, IsUser

class WorkerView(APIView):
    """
    View to list and filter list Workers in the DB
    Required User permission
    """
    serializer_class = WorkerSerializer
    pagination_class = WorkerPagination
    permission_classes = [IsUser, IsAdmin]

    def get(self, request):
        workers = Worker.objects.all()
        filterset = WorkerFilter(request.query_params, queryset=workers)
        if filterset.is_valid():
            queryset = filterset.qs
            paginator = self.pagination_class()
            paginated_qs = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(paginated_qs, many=True)
            return paginator.get_paginated_response()
        (id, first_name, middle_name, last_name, position, is_active)
