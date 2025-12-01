from django.urls import path
from .views import StaffListView, StaffCreateView, StaffUpdateView, StaffDeleteView


urlpatterns = [
    path('', StaffListView.as_view(), name='staff_home'),
    path('add/', StaffCreateView.as_view(), name='staff_add'),
    path('<int:pk>/edit/', StaffUpdateView.as_view(), name='staff_edit'),
    path('<int:pk>/delete/', StaffDeleteView.as_view(), name='staff_delete'),
]


