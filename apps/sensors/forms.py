"""
Sensors app forms - Sensor formalari
"""
from django import forms
from .models import Sensor
import re


class SensorForm(forms.ModelForm):
    """
    Sensor yaratish/tahrirlash formasi
    """
    class Meta:
        model = Sensor
        fields = [
            'device_id', 'name', 'sensor_type', 'lat', 'lon',
            'low_threshold', 'high_threshold', 'unit', 'firmware_ver'
        ]
        widgets = {
            'device_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'sensor_001'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sensor nomi (ixtiyoriy)'
            }),
            'sensor_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'lat': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '41.311081',
                'step': '0.000001'
            }),
            'lon': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '69.240562',
                'step': '0.000001'
            }),
            'low_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pastki chegara',
                'step': '0.01'
            }),
            'high_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Yuqori chegara',
                'step': '0.01'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '%, °C, mm, l/s'
            }),
            'firmware_ver': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'v1.0.0'
            }),
        }

    def clean_device_id(self):
        """
        Device ID faqat harflar, raqamlar va _ bo'lishi kerak
        """
        device_id = self.cleaned_data.get('device_id')
        if not re.match(r'^[a-zA-Z0-9_]+$', device_id):
            raise forms.ValidationError(
                "Qurilma ID faqat harflar, raqamlar va pastki chiziq (_) dan iborat bo'lishi kerak."
            )
        return device_id
