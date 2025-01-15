# Number of workers: For low CPU, stick to 1 worker
workers = 1

# Threads per worker: Set threads to handle multiple I/O-bound tasks
threads = 2

# Worker timeout in seconds: Adjust based on the expected request duration
timeout = 120

# Keep-alive: Set to a reasonable value for connection reuse
keepalive = 5

# Log levels: Helps in debugging and monitoring (can be set to "info" or "debug" as needed)
loglevel = "info"

# Bind to the specified host and port
bind = "0.0.0.0:8000"

# Worker class: "sync" is the default; use "gevent" or "eventlet" for async if your app is I/O-heavy
worker_class = "sync"

# Preload the app to save memory if you're running multiple workers
preload_app = True

# Graceful timeout: Allows workers to cleanly shut down
graceful_timeout = 120
