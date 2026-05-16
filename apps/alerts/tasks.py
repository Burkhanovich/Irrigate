"""
Alerts app Celery vazifalari.
Asosiy vazifalar apps/irrigation/tasks.py da joylashgan.
"""
from apps.irrigation.tasks import check_sensor_thresholds, mark_offline_sensors

__all__ = ['check_sensor_thresholds', 'mark_offline_sensors']
