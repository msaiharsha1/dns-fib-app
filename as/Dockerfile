# Use a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 53533 available (UDP)
EXPOSE 53533/udp

# Run authoritative_server.py when the container launches
CMD ["python", "authoritative_server.py"]
