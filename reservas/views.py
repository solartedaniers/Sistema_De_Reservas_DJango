from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.db.models import Count
from django.db.models.functions import ExtractWeek
from django.db import models
from datetime import timedelta
import io
import json
import pandas as pd
from xhtml2pdf import pisa
from .models import Space, Schedule, Reservation, CustomUser
from .forms import CustomUserCreationForm, ReservationForm, ScheduleForm, SpaceForm
def enviar_recordatorio_reserva(request, pk):
    reserva = get_object_or_404(Reservation, pk=pk)
    if not request.user.is_admin():
        return HttpResponse("No tienes permiso", status=403)
    if reserva.user.email:
        send_mail(
            subject='Recordatorio de reserva',
            message=f'Recuerda tu reserva para el espacio {reserva.space.name} el {reserva.date} en horario {reserva.schedule}.',
            from_email=None,  # usa DEFAULT_FROM_EMAIL
            recipient_list=[reserva.user.email],
        )
        messages.success(request, "¡Recordatorio enviado!")
    else:
        messages.warning(request, "El usuario no tiene correo registrado.")
    return redirect('reservation-list')


def enviar_recordatorios_automaticos(request):
    if not request.user.is_admin():
        return HttpResponse("No tienes permiso", status=403)
    manana = timezone.now().date() + timedelta(days=1)
    reservas = Reservation.objects.filter(date=manana, status='CONFIRMED')
    enviados = 0
    for reserva in reservas:
        if reserva.user.email:
            send_mail(
                subject='Recordatorio de reserva',
                message=f'Recuerda tu reserva para el espacio {reserva.space.name} el {reserva.date} en horario {reserva.schedule}.',
                from_email=None,
                recipient_list=[reserva.user.email],
            )
            enviados += 1
    messages.success(request, f"Se enviaron {enviados} recordatorios para reservas del día siguiente.")
    return redirect('reservation-list')


class RegisterView(generic.CreateView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin()

# Spaces
class SpaceListView(LoginRequiredMixin, generic.ListView):
    model = Space
    template_name = 'spaces/space_list.html'
    paginate_by = 10

class SpaceDetailView(LoginRequiredMixin, generic.DetailView):
    model = Space
    template_name = 'spaces/space_detail.html'

class SpaceCreateView(LoginRequiredMixin, AdminRequiredMixin, generic.CreateView):
    model = Space
    form_class = SpaceForm
    template_name = 'spaces/space_form.html'
    success_url = reverse_lazy('space-list')

class SpaceUpdateView(LoginRequiredMixin, AdminRequiredMixin, generic.UpdateView):
    model = Space
    form_class = SpaceForm
    template_name = 'spaces/space_form.html'
    success_url = reverse_lazy('space-list')

class SpaceDeleteView(LoginRequiredMixin, AdminRequiredMixin, generic.DeleteView):
    model = Space
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('space-list')

# Schedules
class ScheduleListView(LoginRequiredMixin, generic.ListView):
    model = Schedule
    template_name = 'schedules/schedule_list.html'
    paginate_by = 10

class ScheduleCreateView(LoginRequiredMixin, AdminRequiredMixin, generic.CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'schedules/schedule_form.html'
    success_url = reverse_lazy('schedule-list')

class ScheduleUpdateView(LoginRequiredMixin, AdminRequiredMixin, generic.UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'schedules/schedule_form.html'
    success_url = reverse_lazy('schedule-list')

class ScheduleDeleteView(LoginRequiredMixin, AdminRequiredMixin, generic.DeleteView):
    model = Schedule
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('schedule-list')

# Reservations
class ReservationListView(LoginRequiredMixin, generic.ListView):
    model = Reservation
    template_name = 'reservations/reservation_list.html'
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        if not (self.request.user.is_authenticated and self.request.user.is_admin()):
            qs = qs.filter(user=self.request.user)
        return qs.select_related('space', 'schedule', 'user')

class ReservationDetailView(LoginRequiredMixin, generic.DetailView):
    model = Reservation
    template_name = 'reservations/reservation_detail.html'

class ReservationCreateView(LoginRequiredMixin, generic.CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_form.html'
    success_url = reverse_lazy('reservation-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Solicitud de reserva creada, pendiente de confirmación.")
        return super().form_valid(form)

class ReservationUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_form.html'
    success_url = reverse_lazy('reservation-list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not (self.request.user.is_admin() or obj.user == self.request.user):
            messages.error(self.request, "No tienes permiso para editar esta reserva.")
            return redirect('reservation-list')
        return obj

class ReservationDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Reservation
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('reservation-list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not (self.request.user.is_admin() or obj.user == self.request.user):
            messages.error(self.request, "No tienes permiso para eliminar esta reserva.")
            return redirect('reservation-list')
        return obj

# Dashboard
class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dashboard.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_spaces'] = Space.objects.count()
        ctx['total_reservations'] = Reservation.objects.count()
        ctx['recent_reservations'] = Reservation.objects.select_related('space','user').order_by('-created_at')[:8]
        qs = Reservation.objects.all()
        by_month = (qs
                    .annotate(month=models.functions.TruncMonth('date'))
                    .values('month')
                    .annotate(count=Count('id'))
                    .order_by('month') )
        months = [x['month'].strftime('%Y-%m') for x in by_month if x['month']]
        counts = [x['count'] for x in by_month]
        ctx['chart_months'] = json.dumps(months)
        ctx['chart_month_counts'] = json.dumps(counts)
        top_spaces = (Space.objects
                      .annotate(res_count=Count('reservations'))
                      .order_by('-res_count')[:5])
        ctx['top_labels'] = json.dumps([s.name for s in top_spaces])
        ctx['top_values'] = json.dumps([s.res_count for s in top_spaces])
        return ctx

# Utils para filtro de reportes
from django.utils.http import urlencode

def get_filtered_queryset(request):
    qs = Reservation.objects.select_related('space', 'user', 'schedule').all()
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    espacio_id = request.GET.get('espacio')
    estado = request.GET.get('estado')
    if fecha_inicio:
        qs = qs.filter(date__gte=fecha_inicio)
    if fecha_fin:
        qs = qs.filter(date__lte=fecha_fin)
    if espacio_id:
        qs = qs.filter(space_id=espacio_id)
    if estado:
        qs = qs.filter(status=estado)
    return qs

# Reports (solo admin)
def filtrar_reservas(request):
    if not request.user.is_admin():
        return HttpResponse("No tienes permiso", status=403)
    reservas = get_filtered_queryset(request)
    espacios = Space.objects.all()
    return render(request, 'reports/filtrar.html', {
        'reservas': reservas,
        'espacios': espacios
    })

def export_reservations_excel(request):
    if not request.user.is_admin():
        return HttpResponse("No tienes permiso.", status=403)
    qs = get_filtered_queryset(request)
    rows = []
    for r in qs:
        rows.append({
            'id': r.id,
            'user': r.user.username,
            'space': r.space.name,
            'date': r.date,
            'schedule': str(r.schedule),
            'status': r.status,
            'created_at': r.created_at,
        })
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='reservas')
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=reservas.xlsx'
    return response

def export_reservations_pdf(request):
    if not request.user.is_admin():
        return HttpResponse("No tienes permiso.", status=403)
    qs = get_filtered_queryset(request)
    html = render_to_string('reports/reservations_report.html', {'reservations': qs})
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        return HttpResponse("Error al generar PDF", status=500)
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=reservas.pdf'
    return response

def accion_reserva(request, pk):
    reserva = get_object_or_404(Reservation, pk=pk)
    if not request.user.is_admin():
        return HttpResponse("No tienes permiso", status=403)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'confirmar':
            reserva.status = 'CONFIRMED'
            reserva.save()
            messages.success(request, "Reserva confirmada!")
        elif accion == 'rechazar':
            reserva.status = 'REJECTED'
            reserva.save()
            messages.warning(request, "Reserva rechazada!")
    return redirect('reservation-list')

# --- GRÁFICOS ESPECIALES EN EL DASHBOARD ---
class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dashboard.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_spaces'] = Space.objects.count()
        ctx['total_reservations'] = Reservation.objects.count()
        ctx['recent_reservations'] = Reservation.objects.select_related('space','user').order_by('-created_at')[:8]
        qs = Reservation.objects.all()
        by_month = (
            qs.annotate(month=models.functions.TruncMonth('date'))
              .values('month').annotate(count=Count('id')).order_by('month') )
        months = [x['month'].strftime('%Y-%m') for x in by_month if x['month']]
        counts = [x['count'] for x in by_month]
        ctx['chart_months'] = json.dumps(months)
        ctx['chart_month_counts'] = json.dumps(counts)
        top_spaces = (Space.objects
                      .annotate(res_count=Count('reservations'))
                      .order_by('-res_count')[:5])
        ctx['top_labels'] = json.dumps([s.name for s in top_spaces])
        ctx['top_values'] = json.dumps([s.res_count for s in top_spaces])

        # --- GRÁFICO RESERVAS POR SEMANA ---
        by_week = (
            Reservation.objects.filter(status='CONFIRMED')
            .annotate(week=ExtractWeek('date'))
            .values('week').annotate(count=Count('id')).order_by('week')
        )
        ctx['chart_weeks'] = json.dumps([str(x['week']) for x in by_week if x['week']])
        ctx['chart_week_counts'] = json.dumps([x['count'] for x in by_week])

        # --- TASA DE USO POR SALA ---
        total_days = Reservation.objects.values_list('date', flat=True).distinct().count()
        total_slots = Schedule.objects.count() * total_days or 1
        salas = Space.objects.all()
        uso = []
        labels = []
        for s in salas:
            count = Reservation.objects.filter(space=s, status='CONFIRMED').count()
            perc = (count/total_slots)*100 if total_slots else 0
            uso.append(round(perc,1))
            labels.append(s.name)
        ctx['chart_tasa_labels'] = json.dumps(labels)
        ctx['chart_tasa_uso'] = json.dumps(uso)
        return ctx



@login_required
def calendar_view(request):
    reservas = Reservation.objects.select_related('space', 'user').filter(status='CONFIRMED')
    events = []
    is_admin = request.user.is_admin()  # <-- Cambia aquí y pon los paréntesis
    for r in reservas:
        if is_admin:
            events.append({
                'title': f"{r.space.name} - {r.user.username}",
                'start': r.date.strftime('%Y-%m-%d'),
                'color': '#007bff',
            })
        else:
            events.append({
                'title': 'Ocupado',
                'start': r.date.strftime('%Y-%m-%d'),
                'color': '#dc3545',
            })
    reservas_json = mark_safe(json.dumps(events, cls=DjangoJSONEncoder))
    return render(request, 'calendar.html', {'reservas_json': reservas_json, 'is_admin': is_admin})
    