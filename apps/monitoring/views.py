from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from apps.farms.models import Field
from apps.irrigation.models import IrrigationEvent
from apps.alerts.models import Alert


@login_required
def dashboard(request):
    farms = request.user.farms.all()
    active_events = IrrigationEvent.objects.filter(status='running', field__farm__owner=request.user)
    recent_alerts = Alert.objects.filter(field__farm__owner=request.user, is_resolved=False)[:10]
    today = timezone.now().date()
    total_water_today = IrrigationEvent.objects.filter(
        field__farm__owner=request.user,
        started_at__date=today,
        status='completed'
    ).aggregate(total=Sum('water_liters'))['total'] or 0
    
    from apps.sensors.models import Sensor
    offline_sensors = Sensor.objects.filter(field__farm__owner=request.user, status='offline').count()
    
    context = {
        'farms': farms,
        'active_events': active_events,
        'recent_alerts': recent_alerts,
        'total_water_today': total_water_today,
        'offline_sensors': offline_sensors,
    }
    return render(request, 'monitoring/dashboard.html', context)


@login_required
def field_monitoring(request, pk):
    field = get_object_or_404(Field, pk=pk)
    if field.farm.owner != request.user and not request.user.is_admin:
        from django.http import Http404
        raise Http404()
    
    sensors = field.sensors.all()
    latest_readings = {}
    for sensor in sensors:
        reading = sensor.latest_reading()
        if reading:
            latest_readings[sensor.sensor_type] = reading
    
    active_event = field.events.filter(status='running').first()
    schedules = field.schedules.filter(is_active=True)
    
    context = {
        'field': field,
        'sensors': sensors,
        'latest_readings': latest_readings,
        'active_event': active_event,
        'schedules': schedules,
    }
    return render(request, 'monitoring/field_monitoring.html', context)


@login_required
def reports(request):
    field_id = request.GET.get('field_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    events = IrrigationEvent.objects.filter(field__farm__owner=request.user)
    
    if field_id:
        events = events.filter(field_id=field_id)
    if from_date:
        events = events.filter(started_at__date__gte=from_date)
    if to_date:
        events = events.filter(started_at__date__lte=to_date)
    
    total_water = events.aggregate(total=Sum('water_liters'))['total'] or 0
    total_events = events.count()
    
    fields = Field.objects.filter(farm__owner=request.user)
    
    context = {
        'events': events[:50],
        'total_water': total_water,
        'total_events': total_events,
        'fields': fields,
    }
    return render(request, 'monitoring/reports.html', context)
