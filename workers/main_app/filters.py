from django_filters import rest_framework as filters

from .models import Worker

class WorkerFilter(filters.FilterSet):
    position = filters.CharFilter(field_name='position__name', lookup_expr='icontains')
    is_active = filters.BooleanFilter(field_name='is_active')
