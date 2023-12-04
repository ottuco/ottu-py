from .errors import APIInterruptError


def interruption_handler(func):
    """Decorator to handle keyboard interruption."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIInterruptError as e:
            return e.as_dict()

    return wrapper
