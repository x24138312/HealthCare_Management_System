import boto3
from decouple import config

# Initialize DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
    region_name=config('AWS_REGION', default='us-east-1'),
)

def create_patient(patient_id, name, email, phone, doctor_id):
    """
    Create a new patient in the Patients table in DynamoDB.
    """
    table = dynamodb.Table('Patients')
    try:
        table.put_item(
            Item={
                'patient_id': patient_id,
                'name': name,
                'email': email,
                'phone': phone,
                'doctor_id': doctor_id
            }
        )
    except Exception as e:
        print(f"Error creating patient in DynamoDB: {e}")

def get_from_dynamodb(table_name, key):
    """
    Retrieve a single item from a DynamoDB table using the provided key.
    """
    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(Key=key)
        return response.get('Item', {})
    except Exception as e:
        print(f"Error retrieving from DynamoDB: {e}")
        return {}

def scan_dynamodb(table_name):
    """
    Scan the entire DynamoDB table and return all items.
    """
    table = dynamodb.Table(table_name)
    try:
        response = table.scan()
        return response.get('Items', [])
    except Exception as e:
        print(f"Error scanning DynamoDB table {table_name}: {e}")
        return []