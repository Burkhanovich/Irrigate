from django.urls import path
from . import views

urlpatterns = [
    path('', views.farm_list, name='farm-list'),
    path('create/', views.farm_create, name='farm-create'),
    path('<int:pk>/', views.farm_detail, name='farm-detail'),
    path('<int:pk>/edit/', views.farm_update, name='farm-update'),
    path('<int:pk>/delete/', views.farm_delete, name='farm-delete'),
    path('<int:farm_pk>/fields/', views.field_list, name='field-list'),
    path('<int:farm_pk>/fields/create/', views.field_create, name='field-create'),
    path('fields/<int:pk>/', views.field_detail, name='field-detail'),
    path('fields/<int:pk>/edit/', views.field_update, name='field-update'),
    path('fields/<int:pk>/delete/', views.field_delete, name='field-delete'),
]
