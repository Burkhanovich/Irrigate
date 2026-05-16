"""
Farms app models - Ferma va dala modellari
"""
from django.db import models
from django.urls import reverse
from django.conf import settings


UZBEKISTAN_REGIONS = [
    ('tashkent', 'Toshkent'),
    ('tashkent_region', 'Toshkent viloyati'),
    ('andijan', 'Andijon'),
    ('bukhara', 'Buxoro'),
    ('fergana', 'Farg\'ona'),
    ('jizzakh', 'Jizzax'),
    ('kashkadarya', 'Qashqadaryo'),
    ('khorezm', 'Xorazm'),
    ('namangan', 'Namangan'),
    ('navoi', 'Navoiy'),
    ('samarkand', 'Samarqand'),
    ('sirdarya', 'Sirdaryo'),
    ('surkhandarya', 'Surxondaryo'),
    ('karakalpakstan', 'Qoraqalpog\'iston'),
]


class Farm(models.Model):
    """
    Ferma modeli - asosiy xo'jalik birligi
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='farms',
        verbose_name='Egasi'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Ferma nomi'
    )
    region = models.CharField(
        max_length=50,
        choices=UZBEKISTAN_REGIONS,
        verbose_name='Viloyat'
    )
    district = models.CharField(
        max_length=100,
        verbose_name='Tuman'
    )
    lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='Kenglik (latitude)'
    )
    lon = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name='Uzunlik (longitude)'
    )
    total_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Umumiy maydon (gektar)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Tavsif'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan sana'
    )

    class Meta:
        verbose_name = 'Ferma'
        verbose_name_plural = 'Fermalar'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.owner.full_name})"

    def get_absolute_url(self):
        return reverse('farm-detail', kwargs={'pk': self.pk})

    def total_fields(self):
        """Jami dalalar soni"""
        return self.fields.count()


class Field(models.Model):
    """
    Dala modeli - ekin ekiladigan maydon
    """
    CROP_TYPES = [
        ('cotton', 'Paxta'),
        ('wheat', 'Bug\'doy'),
        ('vegetable', 'Sabzavot'),
        ('fruit', 'Meva'),
        ('rice', 'Sholi'),
        ('other', 'Boshqa'),
    ]

    IRR_METHODS = [
        ('drip', 'Tomchilatib sug\'orish'),
        ('sprinkler', 'Yomg\'irlatib sug\'orish'),
        ('surface', 'Sirt sug\'orish'),
        ('subsurface', 'Yer osti sug\'orish'),
    ]

    SOIL_TYPES = [
        ('loam', 'Loy tuproq'),
        ('clay', 'Loy tuproq (og\'ir)'),
        ('sandy', 'Qumli tuproq'),
        ('saline', 'Sho\'r tuproq'),
        ('silty', 'Loyqa tuproq'),
    ]

    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='fields',
        verbose_name='Ferma'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Dala nomi'
    )
    area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Maydon (gektar)'
    )
    crop_type = models.CharField(
        max_length=50,
        choices=CROP_TYPES,
        verbose_name='Ekin turi'
    )
    irr_method = models.CharField(
        max_length=50,
        choices=IRR_METHODS,
        verbose_name='Sug\'orish usuli'
    )
    soil_type = models.CharField(
        max_length=50,
        choices=SOIL_TYPES,
        blank=True,
        verbose_name='Tuproq turi'
    )
    planting_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Ekish sanasi'
    )
    harvest_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Hosilni yig\'ish sanasi'
    )
    polygon_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Dala chegaralari (GeoJSON)'
    )
    kc_value = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.0,
        verbose_name='Ekin koeffitsienti (Kc)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Faol'
    )

    class Meta:
        verbose_name = 'Dala'
        verbose_name_plural = 'Dalalar'
        ordering = ['farm', 'name']

    def __str__(self):
        return f"{self.farm.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('field-detail', kwargs={'pk': self.pk})

    def current_moisture(self):
        """
        Oxirgi tuproq namligi sensor qiymati
        """
        from apps.sensors.models import Sensor, SensorReading

        moisture_sensor = self.sensors.filter(
            sensor_type='soil_moisture',
            status='online'
        ).first()

        if moisture_sensor:
            latest = moisture_sensor.readings.first()
            if latest:
                return latest.value
        return None

    def is_irrigating(self):
        """
        Hozir sug'orilmoqdami
        """
        return self.events.filter(status='running').exists()
