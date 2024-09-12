# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .


# Make port 8000 available to the world outside this container
EXPOSE 8000

# Set the working directory to the foodtales subdirectory
WORKDIR /app/foodtales

# Run the Django development server (or use gunicorn for production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
