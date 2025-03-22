from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    doctor_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    specialization = models.CharField(max_length=100, default="General")  # New field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('NEW', 'New'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
    )
    patient_id = models.CharField(max_length=50)
    doctor_id = models.CharField(max_length=50)
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Appointment for {self.patient_id} on {self.date}"