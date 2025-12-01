from django.shortcuts import render
from django.utils import timezone
from patients.models import Patient
from staff.models import Staff
from appointments.models import Appointment


def home(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    kpis = {
        'patients_total': Patient.objects.count(),
        'staff_total': Staff.objects.count(),
        'appointments_today': Appointment.objects.filter(scheduled_at__date=now.date()).count(),
        'appointments_upcoming': Appointment.objects.filter(scheduled_at__gte=now).count(),
    }

    recent_patients = Patient.objects.order_by('-created_at')[:5]
    upcoming_appointments = Appointment.objects.select_related('patient', 'staff').order_by('scheduled_at')[:5]

    context = {
        'kpis': kpis,
        'recent_patients': recent_patients,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'home.html', context)


