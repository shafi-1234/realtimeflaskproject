# gunicorn.conf.py
timeout = 120  # Increase timeout to 120 seconds
workers = 2   # Adjust workers based on CPU cores
worker_class = 'gevent'  # Use async workers if applicable
