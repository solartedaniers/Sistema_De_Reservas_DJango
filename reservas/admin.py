from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Space, Schedule, Reservation

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Rol', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_staff')

@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'capacity', 'is_active')
    list_filter = ('type', 'is_active')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'description')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('space', 'date', 'schedule', 'user', 'status', 'created_at')
    list_filter = ('status', 'space', 'date')
    search_fields = ('user__username', 'space__name', 'purpose')
