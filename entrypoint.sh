#!/bin/bash
set -e

echo "Running database migrations..."
flask db upgrade

echo "Starting application..."
exec gunicorn --bind=0.0.0.0:5000 "app:create_app()"