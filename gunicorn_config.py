timeout = 120  # Increase timeout to 120 seconds
workers = 1  # Set to 1 worker to minimize CPU usage
worker_class = 'sync'  # Default synchronous workers to reduce overhead
threads = 2  # Use 2 threads for handling concurrent requests within the same worker
