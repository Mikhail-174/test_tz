from django.urls import path
from .views import WorkerView, WorkerIDView, WorkerImportView

urlpatterns = [
    path('', WorkerView.as_view(), name="workers"), #GET, POST
    path('<uuid:id>/', WorkerIDView.as_view(), name="worker_RUD"),
    path('import/', WorkerImportView.as_view(), name="excel_import"), #POST импорт работников из Excel
]