from django.contrib import admin
from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "role", "phone")
    search_fields = ("first_name", "last_name", "phone", "email")
    list_filter = ("role",)
