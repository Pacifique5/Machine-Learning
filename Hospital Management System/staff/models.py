from django.db import models


class Staff(models.Model):
    ROLE_CHOICES = [
        ("DOCTOR", "Doctor"),
        ("NURSE", "Nurse"),
        ("ADMIN", "Admin"),
        ("LAB", "Lab Technician"),
        ("OTHER", "Other"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"
