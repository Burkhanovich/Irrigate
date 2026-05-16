"""
MQTT listener management command.
Ishga tushirish: python manage.py mqtt_listen
"""
import json
import time
import logging
import django
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger('mqtt_listener')


class Command(BaseCommand):
    help = 'MQTT brokerga ulanib sensor ma\'lumotlarini tinglaydi'

    def handle(self, *args, **options):
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            self.stderr.write("paho-mqtt o'rnatilmagan. pip install paho-mqtt")
            return

        self.stdout.write(self.style.SUCCESS("MQTT listener ishga tushmoqda..."))

        client = mqtt.Client(client_id="irrigate_listener", clean_session=True)

        if settings.MQTT_USERNAME:
            client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.on_disconnect = self._on_disconnect

        while True:
            try:
                client.connect(
                    settings.MQTT_HOST,
                    settings.MQTT_PORT,
                    settings.MQTT_KEEPALIVE
                )
                self.stdout.write(f"MQTT ga ulanildi: {settings.MQTT_HOST}:{settings.MQTT_PORT}")
                client.loop_forever()
            except Exception as e:
                logger.error(f"MQTT ulanish xatosi: {e}")
                self.stderr.write(f"Xato: {e}. 5 soniyadan so'ng qayta uriniladi...")
                time.sleep(5)

    @staticmethod
    def _on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT brokerga muvaffaqiyatli ulandi")
            client.subscribe("farm/+/field/+/sensor/+/data")
            logger.info("Subscribed to: farm/+/field/+/sensor/+/data")
        else:
            logger.error(f"MQTT ulanish xatosi, kod: {rc}")

    @staticmethod
    def _on_message(client, userdata, msg):
        """Kelgan MQTT xabarni qayta ishlash"""
        try:
            payload = json.loads(msg.payload.decode('utf-8'))

            device_id = payload.get('device_id')
            value = payload.get('value')
            unit = payload.get('unit', '')

            if not device_id or value is None:
                logger.warning(f"Noto'g'ri payload: {payload}")
                return

            from apps.sensors.models import Sensor, SensorReading
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            try:
                sensor = Sensor.objects.get(device_id=device_id)
            except Sensor.DoesNotExist:
                logger.warning(f"Sensor topilmadi: {device_id}")
                return

            now = timezone.now()
            SensorReading.objects.create(
                sensor=sensor,
                timestamp=now,
                value=value,
                unit=unit or sensor.unit
            )

            Sensor.objects.filter(pk=sensor.pk).update(
                status='online',
                last_seen=now
            )

            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"field_{sensor.field_id}",
                    {
                        'type': 'sensor_reading',
                        'sensor_id': sensor.pk,
                        'sensor_type': sensor.sensor_type,
                        'value': float(value),
                        'unit': unit or sensor.unit,
                        'timestamp': now.isoformat(),
                    }
                )

            from apps.irrigation.tasks import check_sensor_thresholds
            check_sensor_thresholds.apply_async(countdown=5)

            logger.debug(f"Reading saved: {device_id} = {value} {unit}")

        except json.JSONDecodeError:
            logger.error(f"JSON decode xatosi: {msg.payload}")
        except Exception as e:
            logger.error(f"Xabarni qayta ishlashda xato: {e}", exc_info=True)

    @staticmethod
    def _on_disconnect(client, userdata, rc):
        if rc != 0:
            logger.warning(f"MQTT kutilmagan uzilish, kod: {rc}")
