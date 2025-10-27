from django.urls import path
from .views import WorkerView, WorkerIDView

urlpatterns = [
    path('', WorkerView.as_view(), name="workers"), #GET список работников
    path('<uuid:id>/', WorkerIDView.as_view(), name="worker_RUD"),
    #path('/api/workers/import/', views., name=excel_import), POST импорт работников из Excel
]
