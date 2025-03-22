from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from decouple import config
from .models import Appointment, Doctor
from utils.aws_utils import upload_to_s3, send_sns_notification, get_from_dynamodb
from utils.patient_utils import create_patient, get_patient, update_patient, delete_patient
from datetime import datetime
from django.utils import timezone
from utils.dynamodb_utils import scan_dynamodb
from utils.dynamodb_utils import create_patient  # Import create_patient

# Load AWS configurations from .env
BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
SNS_TOPIC_ARN = config('SNS_TOPIC_ARN')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')    

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # Fetch stats for the dashboard
    all_appointments = Appointment.objects.count()
    new_appointments = Appointment.objects.filter(status='NEW').count()
    approved_appointments = Appointment.objects.filter(status='APPROVED').count()
    cancelled_appointments = Appointment.objects.filter(status='CANCELLED').count()
    total_patients = len(scan_dynamodb('Patients'))  # Use scan_dynamodb to count patients
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(user=request.user, date__gte=timezone.now()).order_by('date')[:5]
    
    return render(request, 'dashboard.html', {
        'all_appointments': all_appointments,
        'new_appointments': new_appointments,
        'approved_appointments': approved_appointments,
        'cancelled_appointments': cancelled_appointments,
        'total_patients': total_patients,
        'upcoming_appointments': upcoming_appointments,
    })

@login_required
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctor_list.html', {'doctors': doctors})

@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@login_required
def book_appointment(request):
    if request.method == 'POST':
        doctor_id = request.POST['doctor_id']
        date_str = request.POST['date']
        time_str = request.POST['time']
        patient_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"  # Generate a patient ID
        # Parse the date and make it timezone-aware
        naive_date = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        date = timezone.make_aware(naive_date)  # Make the datetime timezone-aware
        
        # Create patient in DynamoDB
        create_patient(patient_id, "New Patient", "newpatient@example.com", "1234567890", doctor_id)
        
        # Create appointment
        Appointment.objects.create(
            patient_id=patient_id,
            doctor_id=doctor_id,
            date=date,
            user=request.user
        )
        
        # Upload report to S3 if provided
        if 'report' in request.FILES:
            report = request.FILES['report']
            upload_to_s3(report, BUCKET_NAME, f'patient_{patient_id}/{report.name}')
        
        # Send SNS notification
        send_sns_notification(
            SNS_TOPIC_ARN,
            f"New appointment for patient {patient_id} on {date}"
        )
        return redirect('dashboard')
    doctors = Doctor.objects.all()
    return render(request, 'book_appointment.html', {'doctors': doctors})

@login_required
def appointment_history(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'appointment_history.html', {'appointments': appointments})

@login_required
def create_patient_view(request):
    if request.method == 'POST':
        patient_id = request.POST['patient_id']
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        doctor_id = request.POST['doctor_id']
        date = request.POST['date']
        
        if create_patient(patient_id, name, email, phone, doctor_id):
            if 'report' in request.FILES:
                report = request.FILES['report']
                upload_to_s3(report, BUCKET_NAME, f'patient_{patient_id}/{report.name}')
            Appointment.objects.create(
                patient_id=patient_id,
                doctor_id=doctor_id,
                date=date,
                user=request.user
            )
            send_sns_notification(
                SNS_TOPIC_ARN,
                f"Appointment for {name} on {date}"
            )
            return redirect('dashboard')
    return render(request, 'create_patient.html')

@login_required
def read_patient_view(request, patient_id):
    patient = get_patient(patient_id)
    return render(request, 'patient_detail.html', {'patient': patient})

@login_required
def update_patient_view(request, patient_id):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        if update_patient(patient_id, name, email, phone):
            return redirect('dashboard')
    patient = get_patient(patient_id)
    return render(request, 'update_patient.html', {'patient': patient})

@login_required
def delete_patient_view(request, patient_id):
    if delete_patient(patient_id):
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def delete_doctor(request, doctor_id):
    Doctor.objects.filter(doctor_id=doctor_id).delete()
    return redirect('doctor_list')

@login_required
def delete_user(request, user_id):
    User.objects.filter(id=user_id).delete()
    return redirect('user_list')

@login_required
def update_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    if request.method == 'POST':
        status = request.POST['status']
        old_status = appointment.status
        appointment.status = status
        appointment.save()

        # Send SNS notification if status has changed
        if old_status != status:
            message = (
                f"Appointment Status Updated for {request.user.username}\n\n"
                f"Appointment ID: {appointment.patient_id}\n"
                f"New Status: {status}\n"
                f"Date: {appointment.date}\n"
                f"Doctor ID: {appointment.doctor_id}\n\n"
                f"Regards,\nHealthcare Management System"
            )
            send_sns_notification(
                SNS_TOPIC_ARN,
                message
            )
        return redirect('appointment_history')
    return render(request, 'update_appointment.html', {'appointment': appointment})

@login_required
def delete_appointment(request, appointment_id):
    Appointment.objects.filter(id=appointment_id).delete()
    return redirect('appointment_history')

# Add this to patients/views.py
@login_required
def user_appointments(request, user_id):
    user = User.objects.get(id=user_id)
    appointments = Appointment.objects.filter(user=user)
    return render(request, 'user_appointments.html', {'user': user, 'appointments': appointments})   

@login_required
def update_doctor(request, doctor_id):
    doctor = Doctor.objects.get(doctor_id=doctor_id)
    if request.method == 'POST':
        doctor.name = request.POST['name']
        doctor.email = request.POST['email']
        doctor.phone = request.POST['phone']
        doctor.specialization = request.POST['specialization']
        doctor.save()
        return redirect('doctor_list')
    return render(request, 'update_doctor.html', {'doctor': doctor})     