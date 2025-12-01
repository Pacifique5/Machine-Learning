from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Appointment
from .forms import AppointmentForm


class AppointmentListView(ListView):
    model = Appointment
    context_object_name = 'appointments'
    ordering = ['-scheduled_at']
    paginate_by = 10
    template_name = 'appointments/list.html'


class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/form.html'
    success_url = reverse_lazy('appointments_home')


class AppointmentUpdateView(UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/form.html'
    success_url = reverse_lazy('appointments_home')


class AppointmentDeleteView(DeleteView):
    model = Appointment
    template_name = 'appointments/confirm_delete.html'
    success_url = reverse_lazy('appointments_home')
