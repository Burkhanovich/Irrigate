"""
Users app models - Foydalanuvchilar modeli
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Maxsus foydalanuvchi modeli.
    Rol asosida ruxsatlar boshqariladi.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('farmer', 'Fermer'),
        ('operator', 'Operator'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='farmer',
        verbose_name='Rol'
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name='To\'liq ism'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefon'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar'
    )

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.full_name} ({self.username})"

    @property
    def is_admin(self):
        """Administrator ekanligini tekshirish"""
        return self.role == 'admin' or self.is_superuser

    @property
    def is_farmer(self):
        """Fermer ekanligini tekshirish"""
        return self.role == 'farmer'

    @property
    def is_operator(self):
        """Operator ekanligini tekshirish"""
        return self.role == 'operator'
