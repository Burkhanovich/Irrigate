from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('field/<int:pk>/', views.field_monitoring, name='field-monitoring'),
    path('reports/', views.reports, name='reports'),
]
