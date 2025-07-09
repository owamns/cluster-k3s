import multiprocessing

bind = "0.0.0.0:8000"

workers = min(int(multiprocessing.cpu_count() / 2), 4)

loglevel = "info"

accesslog = "-"
errorlog = "-"

timeout = 120
