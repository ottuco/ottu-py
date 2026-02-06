import typing
from dataclasses import asdict, dataclass

import pytest

from ottu.utils.dataclasses import dynamic_asdict, dynamic_dataclass


@dynamic_dataclass
class OpenPerson:
    name: str
    age: int
    address: str | None = None


@dynamic_dataclass
@dataclass
class HybridPerson:
    name: str
    age: int
    address: str | None = None


class TestDynamicDataClass:
    @pytest.mark.parametrize("cls_type", [OpenPerson, HybridPerson])
    def test_access_with_defined_fields(self, cls_type):
        p = cls_type(name="John", age=30, address="123 Main St")
        assert p.name == "John"
        assert p.age == 30
        assert p.address == "123 Main St"

    @pytest.mark.parametrize("cls_type", [OpenPerson, HybridPerson])
    def test_access_with_extra_fields(self, cls_type):
        p = cls_type(name="John", age=30, address="123 Main St", city="New York")
        assert p.name == "John"
        assert p.age == 30
        assert p.address == "123 Main St"
        assert p.city == "New York"

    @pytest.mark.parametrize("cls_type", [OpenPerson, HybridPerson])
    def test_asdict_with_defined_fields(self, cls_type):
        p = cls_type(name="John", age=30, address="123 Main St")
        assert asdict(p) == {"name": "John", "age": 30, "address": "123 Main St"}

    @pytest.mark.parametrize("cls_type", [OpenPerson, HybridPerson])
    def test_asdict_with_extra_fields(self, cls_type):
        p = cls_type(name="John", age=30, address="123 Main St", city="New York")
        assert asdict(p) == {
            # The `asdict(...)` won't return the dynamically added fields
            "name": "John",
            "age": 30,
            "address": "123 Main St",
        }

    @pytest.mark.parametrize("cls_type", [OpenPerson, HybridPerson])
    def test_dynamic_asdict_with_defined_fields(self, cls_type):
        p = cls_type(name="John", age=30, address="123 Main St")
        assert dynamic_asdict(p) == {
            "name": "John",
            "age": 30,
            "address": "123 Main St",
        }

    @pytest.mark.parametrize("cls_type", [OpenPerson, HybridPerson])
    def test_dynamic_asdict_with_extra_fields(self, cls_type):
        p = cls_type(name="John", age=30, address="123 Main St", city="New York")
        assert dynamic_asdict(p) == {
            "name": "John",
            "age": 30,
            "address": "123 Main St",
            "city": "New York",
        }

    @pytest.mark.parametrize("cls_type", [OpenPerson, HybridPerson])
    def test_attribute_error(self, cls_type):
        p = cls_type(name="John", age=30, address="123 Main St")
        with pytest.raises(AttributeError):
            p.unknown_field

    @pytest.mark.parametrize("cls_type", [OpenPerson, HybridPerson])
    def test_set_attribute(self, cls_type):
        p = cls_type(name="John", age=30, address="123 Main St")
        p.city = "New York"
        assert p.city == "New York"
