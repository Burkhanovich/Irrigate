"""
Irrigation app models - Sug'orish jadvali va hodisalar
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class IrrigationSchedule(models.Model):
    """
    Sug'orish jadvali - avtomatik sug'orishni rejalashtirish
    """
    TRIGGER_TYPES = [
        ('time', 'Vaqt bo\'yicha'),
        ('sensor', 'Sensor bo\'yicha'),
        ('weather', 'Ob-havo bo\'yicha'),
    ]

    field = models.ForeignKey(
        'farms.Field',
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Dala'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Jadval nomi'
    )
    trigger_type = models.CharField(
        max_length=20,
        choices=TRIGGER_TYPES,
        default='time',
        verbose_name='Ishga tushirish turi'
    )
    start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Boshlanish vaqti'
    )
    days_of_week = models.JSONField(
        default=list,
        verbose_name='Hafta kunlari',
        help_text='[1,2,3,4,5] - Dushanba-Juma'
    )
    duration_min = models.PositiveIntegerField(
        default=30,
        verbose_name='Davomiyligi (daqiqa)'
    )
    soil_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Tuproq namligi chegarasi (%)',
        help_text='Sensor trigger uchun'
    )
    target_moisture = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Maqsadli namlik (%)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Faol'
    )
    pause_on_rain = models.BooleanField(
        default=True,
        verbose_name='Yomg\'irda to\'xtatish'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Yaratuvchi'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan'
    )

    class Meta:
        verbose_name = 'Sug\'orish jadvali'
        verbose_name_plural = 'Sug\'orish jadvallari'
        ordering = ['field', '-is_active', 'name']

    def __str__(self):
        return f"{self.field.name} - {self.name}"

    def get_days_display(self):
        """Hafta kunlarini matn ko'rinishida"""
        days_map = {
            1: 'Du', 2: 'Se', 3: 'Ch', 4: 'Pa', 5: 'Ju', 6: 'Sh', 7: 'Ya'
        }
        if not self.days_of_week:
            return 'Har kuni'
        return ', '.join([days_map.get(d, str(d)) for d in sorted(self.days_of_week)])

    def should_run_now(self):
        """
        Hozir ishga tushishi kerakmi
        """
        if not self.is_active:
            return False

        now = timezone.localtime()

        if self.trigger_type == 'time':
            if not self.start_time:
                return False

            # Hafta kuni tekshiruvi
            weekday = now.isoweekday()  # 1=Monday, 7=Sunday
            if self.days_of_week and weekday not in self.days_of_week:
                return False

            # Vaqt tekshiruvi (1 daqiqa oralig'ida)
            current_time = now.time()
            start_hour = self.start_time.hour
            start_min = self.start_time.minute

            if current_time.hour == start_hour and current_time.minute == start_min:
                return True

        return False


class IrrigationEvent(models.Model):
    """
    Sug'orish hodisasi - har bir sug'orish jarayoni
    """
    STATUS_CHOICES = [
        ('running', 'Davom etmoqda'),
        ('completed', 'Yakunlandi'),
        ('stopped', 'To\'xtatildi'),
        ('failed', 'Xato'),
    ]

    TRIGGER_TYPES = [
        ('manual', 'Qo\'lda'),
        ('schedule', 'Jadval bo\'yicha'),
        ('sensor', 'Sensor bo\'yicha'),
        ('weather', 'Ob-havo bo\'yicha'),
    ]

    field = models.ForeignKey(
        'farms.Field',
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Dala'
    )
    schedule = models.ForeignKey(
        IrrigationSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        verbose_name='Jadval'
    )
    trigger_type = models.CharField(
        max_length=20,
        choices=TRIGGER_TYPES,
        verbose_name='Ishga tushirish turi'
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Boshlangan vaqt'
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Tugagan vaqt'
    )
    duration_min = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Davomiyligi (daqiqa)'
    )
    water_liters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Sarflangan suv (litr)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='running',
        verbose_name='Holat'
    )
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Boshlagan foydalanuvchi'
    )
    stop_reason = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='To\'xtatish sababi'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Izohlar'
    )

    class Meta:
        verbose_name = 'Sug\'orish hodisasi'
        verbose_name_plural = 'Sug\'orish hodisalari'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.field.name} - {self.started_at.strftime('%d.%m.%Y %H:%M')}"

    def duration_display(self):
        """Davomiylikni matn ko'rinishida"""
        if self.duration_min:
            hours = int(self.duration_min // 60)
            minutes = int(self.duration_min % 60)
            if hours > 0:
                return f"{hours} soat {minutes} daqiqa"
            return f"{minutes} daqiqa"
        return "—"

    def finish(self, reason=''):
        """
        Sug'orishni yakunlash
        """
        self.ended_at = timezone.now()
        self.status = 'completed' if not reason else 'stopped'
        self.stop_reason = reason

        # Davomiylikni hisoblash
        if self.started_at and self.ended_at:
            delta = self.ended_at - self.started_at
            self.duration_min = delta.total_seconds() / 60

        self.save()
