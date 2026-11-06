from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='dashboard'),
    path('export/csv/', views.ExportRegistrationsCSV.as_view(), name='export_csv'),
    path('export/excel/', views.ExportRegistrationsExcel.as_view(), name='export_excel'),
    path('chart-data/', views.ChartDataView.as_view(), name='chart_data'),
]
