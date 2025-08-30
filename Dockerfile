# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Install necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and group
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --create-home appuser

# Set the working directory
WORKDIR /home/appuser/app

# Create the directory for the database
RUN mkdir -p /home/appuser/app/data && chown -R appuser:appgroup /home/appuser/app/data

# Copy the current directory contents into the container
COPY --chown=appuser:appgroup . /home/appuser/app
RUN chown -R appuser:appgroup /home/appuser/app

# Switch to the non-root user
USER appuser

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Expose the application port
EXPOSE 5000

WORKDIR /home/appuser/app/app

# Define environment variables for Django
ENV DJANGO_SETTINGS_MODULE=webpage.settings
ENV PYTHONUNBUFFERED=1
#ENV DEBUG=False

# Define a build argument for the secret key
ARG LOGIN_SECRET_KEY
ENV LOGIN_SECRET_KEY=${LOGIN_SECRET_KEY}

RUN python3 manage.py makemigrations core
RUN python3 manage.py migrate
RUN python3 manage.py collectstatic --noinput

# Run the application with gunicorn
CMD ["python3", "-m", "gunicorn","--chdir", "/home/appuser/app/app",  "--bind", "0.0.0.0:5000", "--workers", "8", "webpage.wsgi:application"]
