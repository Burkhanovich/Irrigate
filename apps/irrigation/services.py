"""
Irrigation services - Sug'orish biznes logikasi
"""
import paho.mqtt.publish as publish
from django.conf import settings
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)


def send_mqtt_command(field_id, device_id, command, params=None):
    """MQTT orqali IoT qurilmaga buyruq yuborish"""
    topic = f"farm/{field_id}/actuator/{device_id}/cmd"
    payload = {
        'cmd': command,
        'ts': int(timezone.now().timestamp())
    }
    if params:
        payload.update(params)
    
    try:
        publish.single(
            topic,
            payload=str(payload),
            hostname=settings.MQTT_HOST,
            port=settings.MQTT_PORT,
            auth={'username': settings.MQTT_USERNAME, 'password': settings.MQTT_PASSWORD} if settings.MQTT_USERNAME else None
        )
        logger.info(f"MQTT command sent: {topic} - {command}")
    except Exception as e:
        logger.error(f"MQTT error: {str(e)}")


def start_field_irrigation(field, duration_min, triggered_by=None, schedule=None):
    """Dalada sug'orishni boshlash"""
    from .models import IrrigationEvent
    
    # Hozir sug'orilayotganini tekshirish
    if field.events.filter(status='running').exists():
        raise ValueError("Dala allaqachon sug'orilmoqda")
    
    # Event yaratish
    event = IrrigationEvent.objects.create(
        field=field,
        schedule=schedule,
        trigger_type='manual' if not schedule else 'schedule',
        started_by=triggered_by,
        status='running'
    )
    
    # MQTT buyrug'i - ventilni ochish
    send_mqtt_command(field.pk, f"valve_{field.pk}", 'open', {'duration': duration_min * 60})
    
    # WebSocket orqali xabar yuborish
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"field_{field.pk}",
            {
                'type': 'irrigation_status',
                'status': 'started',
                'event_id': event.pk
            }
        )
    
    # Celery task - to'xtatish uchun
    try:
        from .tasks import stop_scheduled_irrigation
        stop_scheduled_irrigation.apply_async(
            args=[event.pk, 'schedule_end'],
            countdown=duration_min * 60
        )
    except Exception as e:
        logger.warning(f"Celery task scheduling failed (Redis unavailable?): {e}")

    logger.info(f"Irrigation started for field {field.pk}, event {event.pk}")
    return event


def stop_field_irrigation(event, reason='manual'):
    """Sug'orishni to'xtatish"""
    event.finish(reason=reason)
    
    # MQTT buyrug'i - ventilni yopish
    send_mqtt_command(event.field.pk, f"valve_{event.field.pk}", 'close')
    
    # Suv sarfini hisoblash (flow_meter dan)
    from apps.sensors.models import Sensor
    flow_sensor = event.field.sensors.filter(sensor_type='flow_meter').first()
    if flow_sensor and event.started_at and event.ended_at:
        # Soddalashtirilgan hisoblash
        duration_hours = (event.ended_at - event.started_at).total_seconds() / 3600
        event.water_liters = duration_hours * 1000  # taxminiy
        event.save()
    
    # WebSocket xabar
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"field_{event.field.pk}",
            {
                'type': 'irrigation_status',
                'status': 'stopped',
                'event_id': event.pk
            }
        )
    
    logger.info(f"Irrigation stopped for event {event.pk}")
