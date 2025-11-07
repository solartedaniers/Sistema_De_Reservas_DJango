from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Reservation, Schedule, Space
from django.core.exceptions import ValidationError
from datetime import date

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Por ejemplo: juanperez',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'correo@ejemplo.com',
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Nombre',
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Apellido',
                'class': 'form-control'
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['first_name'].label = 'Nombre(s)'
        self.fields['last_name'].label = 'Apellido(s)'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['username'].help_text = 'Requerido. Solo letras, números y @/./+/-/_.'
        self.fields['email'].help_text = 'Ingresa tu correo. Importante para avisos.'
        self.fields['password1'].help_text = 'Debe tener al menos 8 caracteres.'
        self.fields['password2'].help_text = 'Repite la contraseña.'
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'USER'
        if commit:
            user.save()
        return user

class SpaceForm(forms.ModelForm):
    class Meta:
        model = Space
        fields = ['name', 'type', 'capacity', 'location', 'is_active']
        labels = {
            'name': 'Nombre',
            'type': 'Tipo',
            'capacity': 'Capacidad',
            'location': 'Ubicación',
            'is_active': 'Activo',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Aula 101, Sala B, etc.'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 30'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Edificio A, segundo piso'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['space', 'date', 'schedule', 'purpose']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'purpose': forms.TextInput(attrs={
                'placeholder': 'Motivo de la reserva',
                'class': 'form-control'
            })
        }
        labels = {
            'space': 'Espacio',
            'date': 'Fecha',
            'schedule': 'Horario',
            'purpose': 'Motivo'
        }
    def clean_date(self):
        d = self.cleaned_data['date']
        if d < date.today():
            raise ValidationError("No puedes reservar en fechas pasadas.")
        return d
    def clean(self):
        cleaned = super().clean()
        space = cleaned.get('space')
        date_v = cleaned.get('date')
        schedule = cleaned.get('schedule')
        if space and date_v and schedule:
            exists = Reservation.objects.filter(space=space, date=date_v, schedule=schedule).exists()
            if exists:
                raise ValidationError("Ya existe una reserva para ese espacio, fecha y horario.")
        return cleaned

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['start_time', 'end_time', 'description']
        labels = {
            'start_time': 'Hora de inicio',
            'end_time': 'Hora de fin',
            'description': 'Descripción',
        }
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Turno mañana'}),
        }
