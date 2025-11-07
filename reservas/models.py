from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('USER', 'Usuario'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')

    def is_admin(self):
        return self.role == 'ADMIN' or self.is_staff

class Space(models.Model):
    SPACE_TYPE = (
        ('AULA', 'Aula'),
        ('LAB', 'Laboratorio'),
        ('SALA', 'Sala'),
    )
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    location = models.CharField(max_length=200, blank=True)
    type = models.CharField(max_length=10, choices=SPACE_TYPE)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    def get_absolute_url(self):
        return reverse('space-detail', args=[str(self.id)])

class Schedule(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('start_time', 'end_time')
        ordering = ['start_time']

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmada'),
        ('REJECTED', 'Rechazada'),
    )
    user = models.ForeignKey('reservas.CustomUser', on_delete=models.CASCADE, related_name='reservations')
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='reservations')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    date = models.DateField()
    purpose = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ('space', 'date', 'schedule')

    def __str__(self):
        return f"{self.space.name} - {self.date} ({self.schedule}) - {self.user.username}"
