from django.db import models


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='appointments')
    staff = models.ForeignKey('staff.Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="SCHEDULED")
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        patient_name = str(self.patient) if self.patient_id else "Unknown"
        return f"Appointment for {patient_name} on {self.scheduled_at:%Y-%m-%d %H:%M} ({self.get_status_display()})"
