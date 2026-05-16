"""
Config package initialization.
Celery app ni import qilish.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)
