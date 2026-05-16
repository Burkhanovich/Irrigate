from django.urls import path
from . import views

urlpatterns = [
    path('field/<int:field_pk>/', views.sensor_list, name='sensor-list'),
    path('field/<int:field_pk>/create/', views.sensor_create, name='sensor-create'),
    path('<int:pk>/', views.sensor_detail, name='sensor-detail'),
    path('<int:pk>/edit/', views.sensor_update, name='sensor-update'),
    path('<int:pk>/delete/', views.sensor_delete, name='sensor-delete'),
    path('<int:pk>/readings.json', views.sensor_readings_json, name='sensor-readings-json'),
]
