from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Alert


@login_required
def alert_list(request):
    filter_type = request.GET.get('filter', 'unresolved')
    alerts = Alert.objects.filter(field__farm__owner=request.user)
    
    if filter_type == 'unresolved':
        alerts = alerts.filter(is_resolved=False)
    elif filter_type == 'resolved':
        alerts = alerts.filter(is_resolved=True)
    
    alerts = alerts[:100]
    
    context = {
        'alerts': alerts,
        'filter_type': filter_type,
    }
    return render(request, 'alerts/alert_list.html', context)


@login_required
@require_POST
def alert_resolve(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    if alert.field.farm.owner != request.user and not request.user.is_admin:
        messages.error(request, "Ruxsat yo'q")
        return redirect('alert-list')
    
    alert.resolve(request.user)
    messages.success(request, "Ogohlantirish yopildi")
    return redirect('alert-list')


@login_required
@require_POST
def alert_resolve_all(request):
    alerts = Alert.objects.filter(field__farm__owner=request.user, is_resolved=False)
    count = alerts.count()
    for alert in alerts:
        alert.resolve(request.user)
    messages.success(request, f"{count} ta ogohlantirish yopildi")
    return redirect('alert-list')
