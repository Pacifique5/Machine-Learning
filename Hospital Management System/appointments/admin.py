from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "staff", "scheduled_at", "status")
    list_filter = ("status", "scheduled_at")
    search_fields = ("patient__first_name", "patient__last_name", "staff__first_name", "staff__last_name")
