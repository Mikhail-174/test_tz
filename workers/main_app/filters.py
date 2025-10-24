import django_filters

from .models import Worker

class WorkerFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active", lookup_expr="exact")
    position = django_filters.CharFilter(field_name='position', lookup_expr="exact")

    class Meta:
        model = Worker
        fields = ['is_active', 'position']