FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

WORKDIR /app

RUN pip install --upgrade pip setuptools


COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps


COPY . /app/
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
