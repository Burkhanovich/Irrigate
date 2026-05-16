"""
Sensors app models - Sensor va o'lchov modellari
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta


SENSOR_TYPES = [
    ('soil_moisture', 'Tuproq namligi'),
    ('soil_temp', 'Tuproq harorati'),
    ('air_temp', 'Havo harorati'),
    ('air_humidity', 'Havo namligi'),
    ('rainfall', 'Yog\'ingarchilik'),
    ('flow_meter', 'Suv sarfi'),
    ('solar_rad', 'Quyosh radiatsiyasi'),
]


class Sensor(models.Model):
    """
    Sensor modeli - IoT qurilma
    """
    STATUS_CHOICES = [
        ('online', 'Onlayn'),
        ('offline', 'Oflayn'),
        ('error', 'Xato'),
    ]

    field = models.ForeignKey(
        'farms.Field',
        on_delete=models.CASCADE,
        related_name='sensors',
        verbose_name='Dala'
    )
    device_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Qurilma ID'
    )
    name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Sensor nomi'
    )
    sensor_type = models.CharField(
        max_length=50,
        choices=SENSOR_TYPES,
        verbose_name='Sensor turi'
    )
    lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Kenglik'
    )
    lon = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Uzunlik'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='offline',
        verbose_name='Holat'
    )
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Oxirgi faollik'
    )
    firmware_ver = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Firmware versiyasi'
    )
    secret_key = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='Maxfiy kalit'
    )
    low_threshold = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Pastki chegara'
    )
    high_threshold = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Yuqori chegara'
    )
    unit = models.CharField(
        max_length=20,
        default='',
        blank=True,
        verbose_name='O\'lchov birligi'
    )

    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensorlar'
        ordering = ['field', 'sensor_type']

    def __str__(self):
        name = self.name or self.device_id
        return f"{name} ({self.get_sensor_type_display()})"

    def latest_reading(self):
        """Oxirgi o'lchov"""
        return self.readings.first()

    def readings_last_24h(self):
        """So'nggi 24 soatlik o'lchovlar"""
        since = timezone.now() - timedelta(hours=24)
        return self.readings.filter(timestamp__gte=since)

    def is_online(self):
        """Sensor onlaynmi (10 daqiqa ichida ko'ringan)"""
        if not self.last_seen:
            return False
        return timezone.now() - self.last_seen < timedelta(minutes=10)


class SensorReading(models.Model):
    """
    Sensor o'lchov ma'lumoti
    """
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='readings',
        verbose_name='Sensor'
    )
    timestamp = models.DateTimeField(
        db_index=True,
        verbose_name='Vaqt'
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name='Qiymat'
    )
    unit = models.CharField(
        max_length=20,
        verbose_name='Birlik'
    )
    quality = models.SmallIntegerField(
        default=100,
        verbose_name='Sifat (%)'
    )

    class Meta:
        verbose_name = 'Sensor o\'lchovi'
        verbose_name_plural = 'Sensor o\'lchovlari'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.sensor.device_id} - {self.value} {self.unit} @ {self.timestamp}"
