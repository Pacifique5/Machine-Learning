from django.urls import path
from .views import PatientListView, PatientCreateView, PatientUpdateView, PatientDeleteView


urlpatterns = [
    path('', PatientListView.as_view(), name='patients_home'),
    path('add/', PatientCreateView.as_view(), name='patient_add'),
    path('<int:pk>/edit/', PatientUpdateView.as_view(), name='patient_edit'),
    path('<int:pk>/delete/', PatientDeleteView.as_view(), name='patient_delete'),
]


