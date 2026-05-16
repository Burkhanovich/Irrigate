"""
WebSocket routing configuration.
"""
from django.urls import path
from apps.monitoring.consumers import FieldMonitoringConsumer

websocket_urlpatterns = [
    path('ws/field/<int:field_id>/', FieldMonitoringConsumer.as_asgi()),
]
