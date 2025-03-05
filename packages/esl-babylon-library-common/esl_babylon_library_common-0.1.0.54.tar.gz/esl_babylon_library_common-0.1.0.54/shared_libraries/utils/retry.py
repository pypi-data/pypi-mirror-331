import time
from functools import wraps
from typing import Callable, Any

from shared_libraries.core.logger.create_logger import logger


def retry(max_retries: int,
          exceptions: tuple[type[Exception], ...] = (Exception,),
          delay: int = 0) -> Callable:
    """
    Retry Decorator to reattempt the function if specified exceptions occur.

    :param max_retries: The maximum number of retry attempts.
    :param exceptions: A tuple of exceptions that trigger a retry.
    :param delay: Delay in seconds between retries.

    :return: Callable function wrapped with retry functionality.
    """

    def decorator(func: Callable) -> Callable:

        @wraps(wrapped=func)
        def wrapper(*args,
                    **kwargs) -> Any:
            attempts = 0

            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    message = (f"Something went wrong: {e}. "
                               f"Retry {attempts}/{max_retries} for '{func.__name__}'")
                    logger.exception(msg=message)
                    if attempts == max_retries:
                        message = f"Max retries reached for '{func.__name__}'. Function failed."
                        logger.error(msg=message)
                        raise

                    time.sleep(delay)

        return wrapper

    return decorator
