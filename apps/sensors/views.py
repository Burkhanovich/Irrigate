"""
Sensors app views - Sensor viewlari
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.utils import timezone
from datetime import timedelta
from apps.farms.models import Field
from .models import Sensor, SensorReading
from .forms import SensorForm


def check_sensor_owner(sensor, user):
    """Sensor egasini tekshirish"""
    if sensor.field.farm.owner != user and not user.is_admin:
        raise Http404("Sizda bu sensorga kirish huquqi yo'q.")


@login_required
def sensor_list(request, field_pk):
    """Sensorlar ro'yxati"""
    field = get_object_or_404(Field, pk=field_pk)
    if field.farm.owner != request.user and not request.user.is_admin:
        raise Http404("Sizda bu dalaga kirish huquqi yo'q.")
    
    sensors = field.sensors.all()
    
    context = {
        'field': field,
        'sensors': sensors
    }
    return render(request, 'sensors/sensor_list.html', context)


@login_required
def sensor_create(request, field_pk):
    """Yangi sensor yaratish"""
    field = get_object_or_404(Field, pk=field_pk)
    if field.farm.owner != request.user and not request.user.is_admin:
        raise Http404("Sizda bu dalaga kirish huquqi yo'q.")
    
    if request.method == 'POST':
        form = SensorForm(request.POST)
        if form.is_valid():
            sensor = form.save(commit=False)
            sensor.field = field
            sensor.save()
            messages.success(request, f"Sensor '{sensor.device_id}' muvaffaqiyatli yaratildi!")
            return redirect('sensor-detail', pk=sensor.pk)
        else:
            messages.error(request, "Iltimos, xatolarni to'g'irlang.")
    else:
        form = SensorForm()
    
    return render(request, 'sensors/sensor_form.html', {
        'form': form,
        'field': field,
        'title': 'Yangi sensor'
    })


@login_required
def sensor_detail(request, pk):
    """Sensor tafsilotlari"""
    sensor = get_object_or_404(Sensor, pk=pk)
    check_sensor_owner(sensor, request.user)
    
    # So'nggi 50 ta o'lchov
    recent_readings = sensor.readings.all()[:50]
    
    context = {
        'sensor': sensor,
        'recent_readings': recent_readings,
        'latest': sensor.latest_reading()
    }
    return render(request, 'sensors/sensor_detail.html', context)


@login_required
def sensor_update(request, pk):
    """Sensorni tahrirlash"""
    sensor = get_object_or_404(Sensor, pk=pk)
    check_sensor_owner(sensor, request.user)
    
    if request.method == 'POST':
        form = SensorForm(request.POST, instance=sensor)
        if form.is_valid():
            form.save()
            messages.success(request, "Sensor muvaffaqiyatli yangilandi!")
            return redirect('sensor-detail', pk=sensor.pk)
        else:
            messages.error(request, "Iltimos, xatolarni to'g'irlang.")
    else:
        form = SensorForm(instance=sensor)
    
    return render(request, 'sensors/sensor_form.html', {
        'form': form,
        'sensor': sensor,
        'field': sensor.field,
        'title': 'Sensorni tahrirlash'
    })


@login_required
def sensor_delete(request, pk):
    """Sensorni o'chirish"""
    sensor = get_object_or_404(Sensor, pk=pk)
    check_sensor_owner(sensor, request.user)
    
    if request.method == 'POST':
        device_id = sensor.device_id
        field = sensor.field
        sensor.delete()
        messages.success(request, f"Sensor '{device_id}' o'chirildi.")
        return redirect('sensor-list', field_pk=field.pk)
    
    return render(request, 'sensors/sensor_confirm_delete.html', {'sensor': sensor})


@login_required
def sensor_readings_json(request, pk):
    """
    Sensor o'lchovlarini JSON formatda qaytarish
    Parametrlar: ?from=YYYY-MM-DD&to=YYYY-MM-DD&limit=1000
    """
    sensor = get_object_or_404(Sensor, pk=pk)
    check_sensor_owner(sensor, request.user)
    
    # Parametrlarni olish
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    limit = int(request.GET.get('limit', 1000))
    
    # Queryset yaratish
    readings = sensor.readings.all()
    
    if from_date:
        try:
            from_dt = timezone.datetime.strptime(from_date, '%Y-%m-%d')
            from_dt = timezone.make_aware(from_dt)
            readings = readings.filter(timestamp__gte=from_dt)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_dt = timezone.datetime.strptime(to_date, '%Y-%m-%d')
            to_dt = timezone.make_aware(to_dt) + timedelta(days=1)
            readings = readings.filter(timestamp__lt=to_dt)
        except ValueError:
            pass
    
    readings = readings[:limit]
    
    # JSON formatga o'tkazish
    data = {
        'sensor_id': sensor.pk,
        'device_id': sensor.device_id,
        'sensor_type': sensor.sensor_type,
        'readings': [
            {
                'timestamp': r.timestamp.isoformat(),
                'value': float(r.value),
                'unit': r.unit,
                'quality': r.quality
            }
            for r in readings
        ]
    }
    
    return JsonResponse(data)
