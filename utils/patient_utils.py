from .aws_utils import save_to_dynamodb, get_from_dynamodb, update_in_dynamodb, delete_from_dynamodb
from datetime import datetime
from django.utils import timezone

def create_patient(patient_id, name, email, phone, doctor_id):
    """Create a patient in DynamoDB."""
    patient_data = {
        'patient_id': patient_id,
        'name': name,
        'email': email,
        'phone': phone,
        'doctor_id': doctor_id
    }
    return save_to_dynamodb('Patients', patient_data)

def get_patient(patient_id):
    """Retrieve a patient from DynamoDB."""
    return get_from_dynamodb('Patients', {'patient_id': patient_id})

def update_patient(patient_id, name, email, phone):
    """Update a patient in DynamoDB."""
    update_expression = "SET #n = :n, email = :e, phone = :p"
    attr_names = {'#n': 'name'}
    attr_values = {':n': name, ':e': email, ':p': phone}
    return update_in_dynamodb('Patients', {'patient_id': patient_id}, update_expression, attr_names, attr_values)

def delete_patient(patient_id):
    """Delete a patient from DynamoDB."""
    return delete_from_dynamodb('Patients', {'patient_id': patient_id})


def some_function():
    # This might be generating a naive datetime
    return datetime.now()


def some_function():
    return timezone.now()