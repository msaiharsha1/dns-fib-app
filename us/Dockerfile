# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working dir
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install requirements
RUN pip install --no-cache-dir Flask requests

# Make port 8080 available
EXPOSE 8080

# Run user_server.py when the container launches
CMD ["python", "user_server.py"]
