from dataclasses import asdict, dataclass, field, fields
from typing import Any, Dict, Type, TypeVar

T = TypeVar("T")


def dynamic_dataclass(cls: Type[T]) -> Type[T]:
    """
    A decorator that makes a dataclass accept dynamic fields.

    Args:
        cls: The class to be decorated

    Returns:
        A new dataclass that can accept arbitrary fields
    """
    # First make it a regular dataclass if it isn't already
    if not hasattr(cls, "__dataclass_fields__"):
        cls = dataclass(cls)

    # Store the original class attributes
    original_annotations = getattr(cls, "__annotations__", {}).copy()

    # Initialize the _extra_fields as a class variable with a default factory
    # This fixes the type checking issue
    setattr(cls, "_extra_fields", field(default_factory=dict))
    original_annotations["_extra_fields"] = Dict[str, Any]

    # Store the original __init__
    original_init = cls.__init__

    def __init__(self: Any, **kwargs):
        # Initialize _extra_fields first
        object.__setattr__(self, "_extra_fields", {})

        # Get defined fields
        defined_fields = {f.name for f in fields(self)}

        # Separate known and unknown fields
        known_fields = {k: v for k, v in kwargs.items() if k in defined_fields}
        unknown_fields = {k: v for k, v in kwargs.items() if k not in defined_fields}

        # Initialize with known fields
        original_init(self, **known_fields)

        # Store unknown fields
        self._extra_fields.update(unknown_fields)

    def __getattr__(self: Any, name: str) -> Any:
        if name in self._extra_fields:
            return self._extra_fields[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    def __setattr__(self: Any, name: str, value: Any) -> None:
        if name in {f.name for f in fields(self)} or name == "_extra_fields":
            super(cls, self).__setattr__(name, value)
        else:
            self._extra_fields[name] = value

    # Create new class with dynamic field support
    new_cls = type(
        cls.__name__,
        (cls,),
        {
            "__annotations__": original_annotations,
            "__init__": __init__,
            "__getattr__": __getattr__,
            "__setattr__": __setattr__,
        },
    )

    return new_cls


def dynamic_asdict(obj: Any) -> Dict[str, Any]:
    """
    A function that returns the dataclass fields as a dictionary.

    Args:
        obj: The object to be converted to a dictionary

    Returns:
        A dictionary containing the dataclass fields and values
    """
    data = asdict(obj)
    data.update(obj._extra_fields)
    return data
