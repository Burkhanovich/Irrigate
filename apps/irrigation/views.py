"""
Irrigation app views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from apps.farms.models import Field
from .models import IrrigationSchedule, IrrigationEvent
from .forms import IrrigationScheduleForm, ManualIrrigationForm
from .services import start_field_irrigation, stop_field_irrigation
import logging

logger = logging.getLogger(__name__)


def check_field_owner(field, user):
    if field.farm.owner != user and not user.is_admin:
        raise Http404("Access denied")


@login_required
def schedule_list(request, field_pk):
    field = get_object_or_404(Field, pk=field_pk)
    check_field_owner(field, request.user)
    schedules = field.schedules.all()
    return render(request, 'irrigation/schedule_list.html', {'field': field, 'schedules': schedules})


@login_required
def schedule_create(request, field_pk):
    field = get_object_or_404(Field, pk=field_pk)
    check_field_owner(field, request.user)
    if request.method == 'POST':
        form = IrrigationScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.field = field
            schedule.created_by = request.user
            schedule.save()
            messages.success(request, "Jadval yaratildi!")
            return redirect('schedule-list', field_pk=field.pk)
    else:
        form = IrrigationScheduleForm()
    return render(request, 'irrigation/schedule_form.html', {'form': form, 'field': field})


@login_required
def schedule_update(request, pk):
    schedule = get_object_or_404(IrrigationSchedule, pk=pk)
    check_field_owner(schedule.field, request.user)
    if request.method == 'POST':
        form = IrrigationScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, "Jadval yangilandi!")
            return redirect('schedule-list', field_pk=schedule.field.pk)
    else:
        form = IrrigationScheduleForm(instance=schedule)
    return render(request, 'irrigation/schedule_form.html', {'form': form, 'schedule': schedule, 'field': schedule.field})


@login_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(IrrigationSchedule, pk=pk)
    check_field_owner(schedule.field, request.user)
    if request.method == 'POST':
        field = schedule.field
        schedule.delete()
        messages.success(request, "Jadval o'chirildi.")
        return redirect('schedule-list', field_pk=field.pk)
    return render(request, 'irrigation/schedule_confirm_delete.html', {'schedule': schedule})


@login_required
@require_POST
def schedule_toggle(request, pk):
    schedule = get_object_or_404(IrrigationSchedule, pk=pk)
    check_field_owner(schedule.field, request.user)
    schedule.is_active = not schedule.is_active
    schedule.save()
    return JsonResponse({'status': 'ok', 'is_active': schedule.is_active})


@login_required
def control_panel(request, field_pk):
    field = get_object_or_404(Field, pk=field_pk)
    check_field_owner(field, request.user)
    active_event = field.events.filter(status='running').first()
    schedules = field.schedules.filter(is_active=True)
    recent_events = field.events.all()[:5]
    form = ManualIrrigationForm()
    context = {'field': field, 'active_event': active_event, 'schedules': schedules, 'recent_events': recent_events, 'form': form}
    return render(request, 'irrigation/control_panel.html', context)


@login_required
@require_POST
def start_irrigation(request, field_pk):
    field = get_object_or_404(Field, pk=field_pk)
    check_field_owner(field, request.user)
    form = ManualIrrigationForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'status': 'error', 'error': 'Invalid form'}, status=400)
    try:
        event = start_field_irrigation(field=field, duration_min=form.cleaned_data['duration_min'], triggered_by=request.user, schedule=None)
        if form.cleaned_data.get('notes'):
            event.notes = form.cleaned_data['notes']
            event.save()
        return JsonResponse({'status': 'ok', 'event_id': event.pk})
    except ValueError as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)


@login_required
@require_POST
def stop_irrigation(request, event_pk):
    event = get_object_or_404(IrrigationEvent, pk=event_pk)
    check_field_owner(event.field, request.user)
    if event.status != 'running':
        return JsonResponse({'status': 'error', 'error': 'Not running'}, status=400)
    stop_field_irrigation(event, reason='manual')
    return JsonResponse({'status': 'ok'})


@login_required
def event_history(request, field_pk):
    field = get_object_or_404(Field, pk=field_pk)
    check_field_owner(field, request.user)
    events = field.events.all()[:50]
    return render(request, 'irrigation/event_history.html', {'field': field, 'events': events})


@login_required
def irrigation_status_json(request, field_pk):
    field = get_object_or_404(Field, pk=field_pk)
    check_field_owner(field, request.user)
    active_event = field.events.filter(status='running').first()
    if active_event:
        data = {'is_irrigating': True, 'event_id': active_event.pk, 'started_at': active_event.started_at.isoformat()}
    else:
        data = {'is_irrigating': False}
    return JsonResponse(data)
