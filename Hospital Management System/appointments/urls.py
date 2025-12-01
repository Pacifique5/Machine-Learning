from django.urls import path
from .views import AppointmentListView, AppointmentCreateView, AppointmentUpdateView, AppointmentDeleteView


urlpatterns = [
    path('', AppointmentListView.as_view(), name='appointments_home'),
    path('add/', AppointmentCreateView.as_view(), name='appointment_add'),
    path('<int:pk>/edit/', AppointmentUpdateView.as_view(), name='appointment_edit'),
    path('<int:pk>/delete/', AppointmentDeleteView.as_view(), name='appointment_delete'),
]


