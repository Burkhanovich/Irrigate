from django.contrib import admin
from .models import Farm, Field


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'region', 'total_area', 'created_at']
    list_filter = ['region']
    search_fields = ['name', 'owner__username', 'owner__full_name']
    readonly_fields = ['created_at']


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'farm', 'crop_type', 'irr_method', 'area', 'is_active']
    list_filter = ['crop_type', 'irr_method', 'is_active', 'soil_type']
    search_fields = ['name', 'farm__name']
