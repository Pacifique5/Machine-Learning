from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Patient
from .forms import PatientForm


class PatientListView(ListView):
    model = Patient
    context_object_name = 'patients'
    ordering = ['last_name', 'first_name']
    paginate_by = 10
    template_name = 'patients/list.html'


class PatientCreateView(CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/form.html'
    success_url = reverse_lazy('patients_home')


class PatientUpdateView(UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/form.html'
    success_url = reverse_lazy('patients_home')


class PatientDeleteView(DeleteView):
    model = Patient
    template_name = 'patients/confirm_delete.html'
    success_url = reverse_lazy('patients_home')
