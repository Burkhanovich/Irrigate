"""
Irrigation app forms - Sug'orish formalari
"""
from django import forms
from .models import IrrigationSchedule


class IrrigationScheduleForm(forms.ModelForm):
    """
    Sug'orish jadvali formasi
    """
    DAYS_CHOICES = [
        (1, 'Dushanba'),
        (2, 'Seshanba'),
        (3, 'Chorshanba'),
        (4, 'Payshanba'),
        (5, 'Juma'),
        (6, 'Shanba'),
        (7, 'Yakshanba'),
    ]

    days_of_week = forms.MultipleChoiceField(
        choices=DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label='Hafta kunlari'
    )

    class Meta:
        model = IrrigationSchedule
        fields = [
            'name', 'trigger_type', 'start_time', 'days_of_week',
            'duration_min', 'soil_threshold', 'target_moisture',
            'is_active', 'pause_on_rain'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jadval nomi'
            }),
            'trigger_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'duration_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Daqiqa',
                'min': '1'
            }),
            'soil_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '%',
                'step': '0.1'
            }),
            'target_moisture': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '%',
                'step': '0.1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'pause_on_rain': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.days_of_week:
            self.initial['days_of_week'] = [str(d) for d in self.instance.days_of_week]

    def clean(self):
        cleaned_data = super().clean()
        trigger_type = cleaned_data.get('trigger_type')
        start_time = cleaned_data.get('start_time')
        soil_threshold = cleaned_data.get('soil_threshold')

        if trigger_type == 'time' and not start_time:
            raise forms.ValidationError(
                "Vaqt bo'yicha trigger uchun boshlanish vaqti majburiy."
            )

        if trigger_type == 'sensor' and not soil_threshold:
            raise forms.ValidationError(
                "Sensor bo'yicha trigger uchun tuproq namligi chegarasi majburiy."
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        days = self.cleaned_data.get('days_of_week')
        if days:
            instance.days_of_week = [int(d) for d in days]
        else:
            instance.days_of_week = []
        if commit:
            instance.save()
        return instance


class ManualIrrigationForm(forms.Form):
    """
    Qo'lda sug'orish formasi
    """
    duration_min = forms.IntegerField(
        label='Davomiyligi (daqiqa)',
        min_value=1,
        max_value=480,
        initial=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Daqiqa'
        })
    )
    notes = forms.CharField(
        label='Izohlar',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Qo\'shimcha izohlar (ixtiyoriy)'
        })
    )
