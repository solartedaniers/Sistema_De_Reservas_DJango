from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    # Espacios
    path('spaces/', views.SpaceListView.as_view(), name='space-list'),
    path('spaces/create/', views.SpaceCreateView.as_view(), name='space-create'),
    path('spaces/<int:pk>/', views.SpaceDetailView.as_view(), name='space-detail'),
    path('spaces/<int:pk>/update/', views.SpaceUpdateView.as_view(), name='space-update'),
    path('spaces/<int:pk>/delete/', views.SpaceDeleteView.as_view(), name='space-delete'),
    # Horarios
    path('schedules/', views.ScheduleListView.as_view(), name='schedule-list'),
    path('schedules/create/', views.ScheduleCreateView.as_view(), name='schedule-create'),
    path('schedules/<int:pk>/update/', views.ScheduleUpdateView.as_view(), name='schedule-update'),
    path('schedules/<int:pk>/delete/', views.ScheduleDeleteView.as_view(), name='schedule-delete'),
    # Reservas
    path('reservations/', views.ReservationListView.as_view(), name='reservation-list'),
    path('reservations/create/', views.ReservationCreateView.as_view(), name='reservation-create'),
    path('reservations/<int:pk>/', views.ReservationDetailView.as_view(), name='reservation-detail'),
    path('reservations/<int:pk>/update/', views.ReservationUpdateView.as_view(), name='reservation-update'),
    path('reservations/<int:pk>/delete/', views.ReservationDeleteView.as_view(), name='reservation-delete'),
    # Auth
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    # Reportes y filtros
    path('reports/export_excel/', views.export_reservations_excel, name='export-excel'),
    path('reports/export_pdf/', views.export_reservations_pdf, name='export-pdf'),
    path('reports/filtrar/', views.filtrar_reservas, name='filtrar-reservas'),
    path('reservations/<int:pk>/accion/', views.accion_reserva, name='accion-reserva'),
    path('reservations/<int:pk>/recordar/', views.enviar_recordatorio_reserva, name='recordar-reserva'),
    path('reservations/recordar_automatico/', views.enviar_recordatorios_automaticos, name='recordar-automatico'),
    path('calendario/', views.calendar_view, name='calendar'),



]
