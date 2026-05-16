"""
URL configuration for IrriGate project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    path('auth/', include('apps.users.urls')),
    path('farms/', include('apps.farms.urls')),
    path('sensors/', include('apps.sensors.urls')),
    path('irrigation/', include('apps.irrigation.urls')),
    path('monitoring/', include('apps.monitoring.urls')),
    path('alerts/', include('apps.alerts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "IrriGate Boshqaruv Paneli"
admin.site.site_title = "IrriGate Admin"
admin.site.index_title = "Xush kelibsiz"
