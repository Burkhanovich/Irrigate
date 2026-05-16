"""
Foydalanuvchi rol tekshiruvi uchun dekoratorlar
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Faqat ko'rsatilgan rollardagi foydalanuvchilarga ruxsat berish"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q.")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Faqat adminlarga ruxsat berish"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, "Sizda admin huquqi yo'q.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def farmer_required(view_func):
    """Faqat fermerlarga ruxsat berish"""
    return role_required('farmer', 'admin')(view_func)
