from django.contrib import admin
from .models import Worker, Position

class WorkerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Worker personal info', {"fields": ['first_name', "middle_name", "last_name", "email", "position"]}),
        ('Record info', {"fields": ['id', 'is_active']}),
    ]
    list_display = ['first_name', "last_name", "email", "position", "is_active", 'created_by', 'hired_date', 'is_deleted', "was_hired_recently", 'is_a_developer']
    list_filter = ["position", "hired_date"]
    search_fields = ["first_name", "last_name", "email"]
    list_editable = ['is_active']
    list_select_related = ['position']


    # Только superuser может видеть удалённых работников
    def get_queryset(self, request):
        qs_default = super().get_queryset(request)
        qs = self.model.objects.unfiltered()
        if request.user.is_superuser:
            return qs
        return qs_default

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


class PositionAdmin(admin.ModelAdmin):
    fields = ('name',)

admin.site.register(Worker, WorkerAdmin)
admin.site.register(Position, PositionAdmin)
