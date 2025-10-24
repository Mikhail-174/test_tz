import django_filters

from workers.main_app.models import Worker

class WorkerFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(field_name="is_active")
    is_not_active = django_filters.BooleanFilter(field_name="is_active")
    position = django_filters.CharFilter(field_name='position')

    class Meta:
        model = Worker
        fields = {
            'is_active': ['lt'],
            'is_not_active': ['gt'],
            'position': ['exact'],
        }