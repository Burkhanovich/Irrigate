"""
Users app forms - Foydalanuvchi formalari
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser


class UserLoginForm(AuthenticationForm):
    """
    Tizimga kirish formasi
    """
    username = forms.CharField(
        label='Email yoki foydalanuvchi nomi',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email yoki username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Parol',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parol'
        })
    )


class UserRegisterForm(UserCreationForm):
    """
    Ro'yxatdan o'tish formasi
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    full_name = forms.CharField(
        max_length=200,
        required=True,
        label='To\'liq ism',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'To\'liq ismingiz'
        })
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        initial='farmer',
        label='Rol',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'full_name', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Foydalanuvchi nomi'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parol'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parolni tasdiqlang'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Profil tahrirlash formasi
    """
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone', 'avatar']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'To\'liq ism'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998 XX XXX XX XX'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
