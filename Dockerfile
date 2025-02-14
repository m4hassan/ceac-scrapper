# Use an official Python 3.12 runtime as a parent image
FROM python:3.12-slim

# Set environment variables to avoid Python buffering and to handle errors more gracefully
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies required for Playwright browsers
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    libglib2.0-0 \
    libnss3 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libasound2 \
    libxss1 \
    libxtst6 \
    libappindicator3-1 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-dev \
    libgbm1 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxtst6 \
    libxss1 \
    xvfb  # Added Xvfb for virtual display

# Create and set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install the Python dependencies in the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install

# Copy the rest of the application code into the container at /app/
COPY . /app/

# Install Make utility (since you're using a Makefile)
RUN apt-get update && apt-get install -y make

# Set the entry point for the container (using make to run the project, with Xvfb)
ENTRYPOINT ["make", "run"]

# Expose port (Optional, if your application listens on any port)
# EXPOSE 8080
