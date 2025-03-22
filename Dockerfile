# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Collect static files (if needed)
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 80

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:80", "healthcare_system.wsgi:application"]


#docker build -t healthcare-system-1 .
#docker run -p 80:80 --env-file .env healthcare-system-1 