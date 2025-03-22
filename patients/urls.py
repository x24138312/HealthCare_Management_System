from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/appointments/', views.user_appointments, name='user_appointments'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('appointment-history/', views.appointment_history, name='appointment_history'),
    path('patient/create/', views.create_patient_view, name='create_patient'),
    path('patient/<str:patient_id>/', views.read_patient_view, name='read_patient'),
    path('patient/<str:patient_id>/update/', views.update_patient_view, name='update_patient'),
    path('patient/<str:patient_id>/delete/', views.delete_patient_view, name='delete_patient'),
    path('doctor/<str:doctor_id>/update/', views.update_doctor, name='update_doctor'),  # New URL
    path('doctor/<str:doctor_id>/delete/', views.delete_doctor, name='delete_doctor'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('appointment/<int:appointment_id>/update/', views.update_appointment, name='update_appointment'),
    path('appointment/<int:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),
]