def remove_empty_values(d: dict):
    """
    Removes empty values from a dictionary.
    """
    return {k: v for k, v in d.items() if v}
