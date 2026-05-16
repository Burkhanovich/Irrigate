from django.contrib import admin
from .models import IrrigationSchedule, IrrigationEvent


@admin.register(IrrigationSchedule)
class IrrigationScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'field', 'trigger_type', 'start_time', 'duration_min', 'is_active']
    list_filter = ['trigger_type', 'is_active']
    search_fields = ['name', 'field__name']


@admin.register(IrrigationEvent)
class IrrigationEventAdmin(admin.ModelAdmin):
    list_display = ['field', 'trigger_type', 'started_at', 'ended_at', 'status', 'water_liters']
    list_filter = ['trigger_type', 'status']
    search_fields = ['field__name']
    readonly_fields = ['started_at']
    date_hierarchy = 'started_at'
