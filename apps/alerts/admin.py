from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['alert_type', 'severity', 'field', 'sensor', 'is_resolved', 'created_at']
    list_filter = ['severity', 'is_resolved', 'alert_type']
    search_fields = ['field__name', 'message']
    readonly_fields = ['created_at', 'resolved_at']
    date_hierarchy = 'created_at'
