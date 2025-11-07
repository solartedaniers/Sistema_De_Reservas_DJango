from django.core.management.base import BaseCommand
from reservas.models import Reservation
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Envia recordatorios automáticos por correo a reservas del día siguiente.'

    def handle(self, *args, **options):
        manana = timezone.now().date() + timedelta(days=1)
        reservas = Reservation.objects.filter(date=manana, status='CONFIRMED')
        enviados = 0
        for reserva in reservas:
            user_email = reserva.user.email
            if user_email:
                send_mail(
                    subject='Recordatorio de reserva',
                    message=f'Recuerda tu reserva para el espacio {reserva.space.name} el {reserva.date} en horario {reserva.schedule}.',
                    from_email=None,
                    recipient_list=[user_email],
                )
                enviados += 1
        self.stdout.write(self.style.SUCCESS(f'Se enviaron {enviados} recordatorios automáticos.'))
