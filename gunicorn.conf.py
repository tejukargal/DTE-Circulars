"""
Gunicorn configuration for Railway deployment
"""

# Server socket
bind = "0.0.0.0:8080"

# Worker processes
workers = 1
worker_class = "sync"
worker_connections = 1000

# Timeout settings - increased for web scraping
timeout = 120  # 2 minutes for worker timeout
keepalive = 5
max_requests = 1000
max_requests_jitter = 100

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "dte-circulars"

# Preload app for better performance
preload_app = True