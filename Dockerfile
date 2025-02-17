# Use official Playwright image (based on Ubuntu 24.04 Noble)
FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

# Set working directory
WORKDIR /app

# Ensure pip and setuptools are up to date
RUN pip install --upgrade pip setuptools


COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps


COPY . /app/

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
