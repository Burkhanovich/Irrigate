"""
Alerts app models - Ogohlantirishlar modeli
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


ALERT_TYPES = [
    ('low_moisture', 'Tuproq namligi past'),
    ('high_moisture', 'Tuproq namligi yuqori'),
    ('device_offline', 'Qurilma offline'),
    ('irrigation_failed', 'Sug\'orish xatosi'),
    ('rain_detected', 'Yomg\'ir aniqlandi'),
    ('low_battery', 'Batareya past'),
]

SEVERITY_CHOICES = [
    ('info', 'Ma\'lumot'),
    ('warning', 'Ogohlantirish'),
    ('critical', 'Muhim'),
]


class Alert(models.Model):
    """
    Ogohlantirish modeli - tizim hodisalari
    """
    field = models.ForeignKey(
        'farms.Field',
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name='Dala'
    )
    sensor = models.ForeignKey(
        'sensors.Sensor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts',
        verbose_name='Sensor'
    )
    alert_type = models.CharField(
        max_length=50,
        choices=ALERT_TYPES,
        verbose_name='Ogohlantirish turi'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        verbose_name='Jiddiylik darajasi'
    )
    message = models.TextField(
        verbose_name='Xabar'
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name='Qiymat'
    )
    threshold = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name='Chegara'
    )
    is_resolved = models.BooleanField(
        default=False,
        verbose_name='Hal qilindi'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan'
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Hal qilingan vaqt'
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
        verbose_name='Hal qilgan foydalanuvchi'
    )

    class Meta:
        verbose_name = 'Ogohlantirish'
        verbose_name_plural = 'Ogohlantirishlar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.field.name}"

    def resolve(self, user):
        """
        Ogohlantirishni yopish
        """
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()
