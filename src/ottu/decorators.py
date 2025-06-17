import inspect

from .errors import APIInterruptError


def interruption_handler(func):
    """Decorator to handle keyboard interruption."""

    if inspect.iscoroutinefunction(func):

        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except APIInterruptError as e:
                return e.as_dict()

        return wrapper
    else:

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except APIInterruptError as e:
                return e.as_dict()

        return wrapper
