from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Staff
from .forms import StaffForm


class StaffListView(ListView):
    model = Staff
    context_object_name = 'staff_members'
    ordering = ['last_name', 'first_name']
    paginate_by = 10
    template_name = 'staff/list.html'


class StaffCreateView(CreateView):
    model = Staff
    form_class = StaffForm
    template_name = 'staff/form.html'
    success_url = reverse_lazy('staff_home')


class StaffUpdateView(UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'staff/form.html'
    success_url = reverse_lazy('staff_home')


class StaffDeleteView(DeleteView):
    model = Staff
    template_name = 'staff/confirm_delete.html'
    success_url = reverse_lazy('staff_home')
