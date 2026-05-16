from django.contrib import admin
from .models import Sensor, SensorReading


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'name', 'sensor_type', 'field', 'status', 'last_seen']
    list_filter = ['sensor_type', 'status']
    search_fields = ['device_id', 'name', 'field__name']
    readonly_fields = ['last_seen']


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'timestamp', 'value', 'unit', 'quality']
    list_filter = ['sensor__sensor_type']
    search_fields = ['sensor__device_id']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
