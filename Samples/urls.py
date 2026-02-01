from django.urls import path
from .views import SampleListCreateAPIView, SampleRetrieveUpdateDestroyAPIView, sample_list_view, add_sample_view, sample_full_screen_view, dashboard_view, export_samples_view, reports_view, export_reports_excel, export_reports_pdf

urlpatterns = [
    path('samples/', SampleListCreateAPIView.as_view(), name='sample-list-create'),
    path('samples/<int:pk>/', SampleRetrieveUpdateDestroyAPIView.as_view(), name='sample-detail'),
    path('samples/web/', sample_list_view, name='sample-list-web'),
    path('samples/add/', add_sample_view, name='add_sample'),
    path('samples/full/<str:sample_number>/', sample_full_screen_view, name='sample_full_screen'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('samples/export/', export_samples_view, name='sample-export'),
    path('reports/', reports_view, name='reports'),
    path('reports/export/excel/', export_reports_excel, name='reports-export-excel'),
    path('reports/export/pdf/', export_reports_pdf, name='reports-export-pdf'),
]
