import time
from functools import wraps

from shared_libraries.utils.color_print import cprint


def measure_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cprint(f"Starting {func.__name__}...")
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        cprint(f"{func.__name__} finished in {elapsed_time:.2f} seconds.")
        return result

    return wrapper
