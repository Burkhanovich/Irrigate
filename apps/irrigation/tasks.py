"""
Celery vazifalar - sug'orish va sensor monitoring
"""
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(name='irrigation.check_time_schedules')
def check_time_schedules():
    """Har 1 daqiqada: vaqt bo'yicha jadvallarni tekshirish"""
    from apps.irrigation.models import IrrigationSchedule
    from apps.irrigation.services import start_field_irrigation

    now = timezone.localtime()
    schedules = IrrigationSchedule.objects.filter(
        is_active=True,
        trigger_type='time'
    ).select_related('field')

    started = 0
    for schedule in schedules:
        try:
            if schedule.should_run_now():
                if not schedule.field.is_irrigating():
                    start_field_irrigation(
                        field=schedule.field,
                        duration_min=schedule.duration_min,
                        schedule=schedule
                    )
                    started += 1
                    logger.info(f"Auto-started irrigation: schedule={schedule.pk}, field={schedule.field.pk}")
        except Exception as e:
            logger.error(f"Error starting scheduled irrigation {schedule.pk}: {e}")

    return f"Checked {schedules.count()} schedules, started {started}"


@shared_task(name='irrigation.check_sensor_triggers')
def check_sensor_triggers():
    """Har 5 daqiqada: sensor trigger jadvallarini tekshirish"""
    from apps.irrigation.models import IrrigationSchedule
    from apps.irrigation.services import start_field_irrigation

    schedules = IrrigationSchedule.objects.filter(
        is_active=True,
        trigger_type='sensor',
        soil_threshold__isnull=False
    ).select_related('field')

    started = 0
    for schedule in schedules:
        try:
            if schedule.field.is_irrigating():
                continue

            moisture = schedule.field.current_moisture()
            if moisture is None:
                continue

            if float(moisture) < float(schedule.soil_threshold):
                start_field_irrigation(
                    field=schedule.field,
                    duration_min=schedule.duration_min,
                    schedule=schedule
                )
                started += 1
                logger.info(f"Sensor-triggered irrigation: field={schedule.field.pk}, moisture={moisture}")
        except Exception as e:
            logger.error(f"Error in sensor trigger check {schedule.pk}: {e}")

    return f"Checked {schedules.count()} sensor schedules, started {started}"


@shared_task(name='irrigation.stop_scheduled_irrigation')
def stop_scheduled_irrigation(event_id, reason='schedule_end'):
    """Sug'orish davomiyligi tugagach to'xtatish"""
    from apps.irrigation.models import IrrigationEvent
    from apps.irrigation.services import stop_field_irrigation

    try:
        event = IrrigationEvent.objects.get(pk=event_id)
        if event.status == 'running':
            stop_field_irrigation(event, reason=reason)
            logger.info(f"Scheduled stop completed: event={event_id}, reason={reason}")
        else:
            logger.info(f"Event {event_id} already stopped (status={event.status})")
    except IrrigationEvent.DoesNotExist:
        logger.warning(f"IrrigationEvent {event_id} not found")


@shared_task(name='alerts.check_sensor_thresholds')
def check_sensor_thresholds():
    """Har 5 daqiqada: sensorlar threshold holatini tekshirish"""
    from apps.sensors.models import Sensor
    from apps.alerts.models import Alert

    sensors = Sensor.objects.filter(
        status='online'
    ).exclude(
        low_threshold=None,
        high_threshold=None
    ).select_related('field')

    alerts_created = 0
    one_hour_ago = timezone.now() - timedelta(hours=1)

    for sensor in sensors:
        latest = sensor.latest_reading()
        if not latest:
            continue

        value = float(latest.value)

        if sensor.low_threshold and value < float(sensor.low_threshold):
            existing = Alert.objects.filter(
                sensor=sensor,
                alert_type='low_moisture',
                is_resolved=False,
                created_at__gte=one_hour_ago
            ).exists()
            if not existing:
                Alert.objects.create(
                    field=sensor.field,
                    sensor=sensor,
                    alert_type='low_moisture',
                    severity='warning',
                    message=f"{sensor.get_sensor_type_display()} past: {value} {sensor.unit} (chegara: {sensor.low_threshold})",
                    value=value,
                    threshold=sensor.low_threshold
                )
                alerts_created += 1

        if sensor.high_threshold and value > float(sensor.high_threshold):
            existing = Alert.objects.filter(
                sensor=sensor,
                alert_type='high_moisture',
                is_resolved=False,
                created_at__gte=one_hour_ago
            ).exists()
            if not existing:
                Alert.objects.create(
                    field=sensor.field,
                    sensor=sensor,
                    alert_type='high_moisture',
                    severity='warning',
                    message=f"{sensor.get_sensor_type_display()} yuqori: {value} {sensor.unit} (chegara: {sensor.high_threshold})",
                    value=value,
                    threshold=sensor.high_threshold
                )
                alerts_created += 1

    return f"Threshold check done, created {alerts_created} alerts"


@shared_task(name='sensors.mark_offline_sensors')
def mark_offline_sensors():
    """Har 10 daqiqada: uzoq ko'rinmagan sensorlarni offline belgilash"""
    from apps.sensors.models import Sensor
    from apps.alerts.models import Alert

    threshold = timezone.now() - timedelta(minutes=15)

    offline_sensors = Sensor.objects.filter(
        status='online',
        last_seen__lt=threshold
    )

    count = 0
    one_hour_ago = timezone.now() - timedelta(hours=1)

    for sensor in offline_sensors:
        sensor.status = 'offline'
        sensor.save(update_fields=['status'])

        existing_alert = Alert.objects.filter(
            sensor=sensor,
            alert_type='device_offline',
            is_resolved=False,
            created_at__gte=one_hour_ago
        ).exists()

        if not existing_alert:
            Alert.objects.create(
                field=sensor.field,
                sensor=sensor,
                alert_type='device_offline',
                severity='critical',
                message=f"Sensor '{sensor.name or sensor.device_id}' 15 daqiqadan beri aloqada yo'q",
            )

        count += 1

    if count:
        logger.warning(f"Marked {count} sensors as offline")

    return f"Marked {count} sensors offline"
