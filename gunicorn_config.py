import multiprocessing

# Server socket
bind = "0.0.0.0:8000"  # Binding to all available IP addresses on port 8000

# Worker settings
workers = 1  # Use a single worker due to limited CPU cores
worker_class = 'sync'  # Use synchronous worker to keep resource usage low

# Log settings
accesslog = '-'  # '-' means logging to stdout (you can change this to a file path)
errorlog = '-'  # '-' means logging to stderr (you can change this to a file path)
loglevel = 'info'  # You can adjust the log level based on your needs

# Timeout settings
timeout = 120  # Timeout in seconds for workers to finish processing

# Worker connection settings
worker_connections = 100  # Max number of simultaneous clients for async workers (if used)

# Keep-alive settings
keepalive = 2  # Keep connections alive for 2 seconds

# Daemonize Gunicorn (run in the background)
daemon = False  # Set to True to run Gunicorn as a daemon

# Enable graceful reloads on code changes
reload = True  # Set to False to disable reloading, True enables auto-reload

# Preload the app to improve startup performance
preload_app = True
