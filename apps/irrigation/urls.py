from django.urls import path
from . import views

urlpatterns = [
    path('field/<int:field_pk>/schedules/', views.schedule_list, name='schedule-list'),
    path('field/<int:field_pk>/schedules/create/', views.schedule_create, name='schedule-create'),
    path('schedules/<int:pk>/edit/', views.schedule_update, name='schedule-update'),
    path('schedules/<int:pk>/delete/', views.schedule_delete, name='schedule-delete'),
    path('schedules/<int:pk>/toggle/', views.schedule_toggle, name='schedule-toggle'),
    path('field/<int:field_pk>/control/', views.control_panel, name='control-panel'),
    path('field/<int:field_pk>/start/', views.start_irrigation, name='start-irrigation'),
    path('event/<int:event_pk>/stop/', views.stop_irrigation, name='stop-irrigation'),
    path('field/<int:field_pk>/history/', views.event_history, name='event-history'),
    path('field/<int:field_pk>/status.json', views.irrigation_status_json, name='irrigation-status-json'),
]
