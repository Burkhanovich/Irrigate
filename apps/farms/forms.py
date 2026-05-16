"""
Farms app forms - Ferma va dala formalari
"""
from django import forms
from .models import Farm, Field


class FarmForm(forms.ModelForm):
    """
    Ferma yaratish/tahrirlash formasi
    """
    class Meta:
        model = Farm
        fields = ['name', 'region', 'district', 'lat', 'lon', 'total_area', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ferma nomi'
            }),
            'region': forms.Select(attrs={
                'class': 'form-select'
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tuman nomi'
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
            'total_area': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Gektar',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ferma haqida qisqacha ma\'lumot'
            }),
        }


class FieldForm(forms.ModelForm):
    """
    Dala yaratish/tahrirlash formasi
    """
    class Meta:
        model = Field
        fields = [
            'name', 'area', 'crop_type', 'irr_method', 'soil_type',
            'planting_date', 'harvest_date', 'kc_value', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dala nomi'
            }),
            'area': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Gektar',
                'step': '0.01'
            }),
            'crop_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'irr_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'soil_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'planting_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'harvest_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'kc_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '2'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        planting_date = cleaned_data.get('planting_date')
        harvest_date = cleaned_data.get('harvest_date')

        if planting_date and harvest_date:
            if harvest_date <= planting_date:
                raise forms.ValidationError(
                    "Hosilni yig'ish sanasi ekish sanasidan keyinroq bo'lishi kerak."
                )

        return cleaned_data
