from django.urls import path
from . import views

urlpatterns = [
    path('', views.alert_list, name='alert-list'),
    path('<int:pk>/resolve/', views.alert_resolve, name='alert-resolve'),
    path('resolve-all/', views.alert_resolve_all, name='alert-resolve-all'),
]
