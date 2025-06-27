# FunTime Scheduler - Gunicorn Configuration File
# For production deployment on Raspberry Pi

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Maximum requests before worker restart
max_requests = 1000
max_requests_jitter = 50

# Preload application for better performance
preload_app = True

# Logging
accesslog = '/opt/funtime-scheduler/logs/access.log'
errorlog = '/opt/funtime-scheduler/logs/error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'funtime-scheduler'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Restart workers after this many seconds
max_worker_memory = 100  # MB
worker_tmp_dir = '/dev/shm'  # Use memory for worker temp files

# Graceful timeout
graceful_timeout = 30

# Environment variables
raw_env = [
    'FLASK_ENV=production',
]
