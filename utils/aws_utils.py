import boto3
from botocore.exceptions import ClientError
import re
from django.conf import settings

# AWS Clients (initialized without hardcoding)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3')
sns = boto3.client('sns', region_name='us-east-1')

def save_to_dynamodb(table_name, item):
    """Save an item to a DynamoDB table."""
    table = dynamodb.Table(table_name)
    try:
        table.put_item(Item=item)
        return True
    except ClientError as e:
        print(f"Error saving to DynamoDB: {e}")
        return False

def get_from_dynamodb(table_name, key):
    """Retrieve an item from a DynamoDB table."""
    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(Key=key)
        return response.get('Item', {})
    except ClientError as e:
        print(f"Error retrieving from DynamoDB: {e}")
        return {}

def update_in_dynamodb(table_name, key, update_expression, attr_names, attr_values):
    """Update an item in a DynamoDB table."""
    table = dynamodb.Table(table_name)
    try:
        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values
        )
        return True
    except ClientError as e:
        print(f"Error updating DynamoDB: {e}")
        return False

def delete_from_dynamodb(table_name, key):
    """Delete an item from a DynamoDB table."""
    table = dynamodb.Table(table_name)
    try:
        table.delete_item(Key=key)
        return True
    except ClientError as e:
        print(f"Error deleting from DynamoDB: {e}")
        return False

def upload_to_s3(file_obj, bucket_name, key):
    # Validate bucket name
    if not re.match(r'^[a-zA-Z0-9._-]{1,255}$', bucket_name):  
        raise ValueError(f"Invalid S3 bucket name: {bucket_name}. Must match regex '^[a-zA-Z0-9._-]{{1,255}}$'")

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    try:
        s3.upload_fileobj(file_obj, bucket_name, key)
    except ClientError as e:
        raise Exception(f"Failed to upload file to S3: {str(e)}")

def send_sns_notification(topic_arn, message):
    """Send a notification via SNS."""
    try:
        sns.publish(TopicArn=topic_arn, Message=message)
        return True
    except ClientError as e:
        print(f"Error sending SNS notification: {e}")
        return False