#!/bin/bash

# FunTime Scheduler - Gunicorn Production Configuration
# This script starts the application with Gunicorn

# Change to application directory
cd /opt/funtime-scheduler

# Activate virtual environment
source venv/bin/activate

# Start Gunicorn with production settings
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --worker-class sync \
    --timeout 120 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --capture-output \
    app:app
