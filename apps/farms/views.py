"""
Farms app views - Ferma va dala viewlari
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .models import Farm, Field
from .forms import FarmForm, FieldForm


def check_farm_owner(farm, user):
    """Ferma egasini tekshirish"""
    if farm.owner != user and not user.is_admin:
        raise Http404("Sizda bu fermaga kirish huquqi yo'q.")


def check_field_owner(field, user):
    """Dala egasini tekshirish"""
    if field.farm.owner != user and not user.is_admin:
        raise Http404("Sizda bu dalaga kirish huquqi yo'q.")


@login_required
def farm_list(request):
    """Fermalar ro'yxati"""
    farms = request.user.farms.all()
    context = {
        'farms': farms
    }
    return render(request, 'farms/farm_list.html', context)


@login_required
def farm_create(request):
    """Yangi ferma yaratish"""
    if request.method == 'POST':
        form = FarmForm(request.POST)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.owner = request.user
            farm.save()
            messages.success(request, f"Ferma '{farm.name}' muvaffaqiyatli yaratildi!")
            return redirect('farm-detail', pk=farm.pk)
        else:
            messages.error(request, "Iltimos, xatolarni to'g'irlang.")
    else:
        form = FarmForm()
    
    return render(request, 'farms/farm_form.html', {'form': form, 'title': 'Yangi ferma'})


@login_required
def farm_detail(request, pk):
    """Ferma tafsilotlari"""
    farm = get_object_or_404(Farm, pk=pk)
    check_farm_owner(farm, request.user)
    
    fields = farm.fields.all()
    
    context = {
        'farm': farm,
        'fields': fields
    }
    return render(request, 'farms/farm_detail.html', context)


@login_required
def farm_update(request, pk):
    """Fermani tahrirlash"""
    farm = get_object_or_404(Farm, pk=pk)
    check_farm_owner(farm, request.user)
    
    if request.method == 'POST':
        form = FarmForm(request.POST, instance=farm)
        if form.is_valid():
            form.save()
            messages.success(request, "Ferma muvaffaqiyatli yangilandi!")
            return redirect('farm-detail', pk=farm.pk)
        else:
            messages.error(request, "Iltimos, xatolarni to'g'irlang.")
    else:
        form = FarmForm(instance=farm)
    
    return render(request, 'farms/farm_form.html', {
        'form': form,
        'title': 'Fermani tahrirlash',
        'farm': farm
    })


@login_required
def farm_delete(request, pk):
    """Fermani o'chirish"""
    farm = get_object_or_404(Farm, pk=pk)
    check_farm_owner(farm, request.user)
    
    if request.method == 'POST':
        farm_name = farm.name
        farm.delete()
        messages.success(request, f"Ferma '{farm_name}' o'chirildi.")
        return redirect('farm-list')
    
    return render(request, 'farms/farm_confirm_delete.html', {'farm': farm})


@login_required
def field_list(request, farm_pk):
    """Dala ro'yxati"""
    farm = get_object_or_404(Farm, pk=farm_pk)
    check_farm_owner(farm, request.user)
    
    fields = farm.fields.all()
    
    context = {
        'farm': farm,
        'fields': fields
    }
    return render(request, 'farms/field_list.html', context)


@login_required
def field_create(request, farm_pk):
    """Yangi dala yaratish"""
    farm = get_object_or_404(Farm, pk=farm_pk)
    check_farm_owner(farm, request.user)
    
    if request.method == 'POST':
        form = FieldForm(request.POST)
        if form.is_valid():
            field = form.save(commit=False)
            field.farm = farm
            field.save()
            messages.success(request, f"Dala '{field.name}' muvaffaqiyatli yaratildi!")
            return redirect('field-detail', pk=field.pk)
        else:
            messages.error(request, "Iltimos, xatolarni to'g'irlang.")
    else:
        form = FieldForm()
    
    return render(request, 'farms/field_form.html', {
        'form': form,
        'farm': farm,
        'title': 'Yangi dala'
    })


@login_required
def field_detail(request, pk):
    """Dala tafsilotlari"""
    field = get_object_or_404(Field, pk=pk)
    check_field_owner(field, request.user)
    
    sensors = field.sensors.all()
    schedules = field.schedules.filter(is_active=True)[:5]
    recent_events = field.events.all()[:5]
    
    context = {
        'field': field,
        'sensors': sensors,
        'schedules': schedules,
        'recent_events': recent_events,
        'current_moisture': field.current_moisture(),
        'is_irrigating': field.is_irrigating()
    }
    return render(request, 'farms/field_detail.html', context)


@login_required
def field_update(request, pk):
    """Dalani tahrirlash"""
    field = get_object_or_404(Field, pk=pk)
    check_field_owner(field, request.user)
    
    if request.method == 'POST':
        form = FieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            messages.success(request, "Dala muvaffaqiyatli yangilandi!")
            return redirect('field-detail', pk=field.pk)
        else:
            messages.error(request, "Iltimos, xatolarni to'g'irlang.")
    else:
        form = FieldForm(instance=field)
    
    return render(request, 'farms/field_form.html', {
        'form': form,
        'field': field,
        'title': 'Dalani tahrirlash'
    })


@login_required
def field_delete(request, pk):
    """Dalani o'chirish"""
    field = get_object_or_404(Field, pk=pk)
    check_field_owner(field, request.user)
    
    if request.method == 'POST':
        field_name = field.name
        farm = field.farm
        field.delete()
        messages.success(request, f"Dala '{field_name}' o'chirildi.")
        return redirect('farm-detail', pk=farm.pk)
    
    return render(request, 'farms/field_confirm_delete.html', {'field': field})
