"""Test serializers module."""

import pytest

from dataclasses import dataclass

from serious_serializers.serializers import SlotsSerializer


@dataclass(slots=True)
class Parameters(SlotsSerializer):
    a: int
    b: float
    c: str


SIMPLE = Parameters(2, 0.0, "abc")

SIMPLE_ARGS = [
    ("a", 2),
    ("b", 0.0),
    ("c", "abc"),
]


SIMPLE_YAML = "a: 2\nb: 0.0\nc: abc\n"


def test_simple_to_dict():
    """Test `to_dict` method for simple class."""
    params_dict = SIMPLE.to_dict()
    for k, v in SIMPLE_ARGS:
        assert params_dict[k] == v


def test_simple_to_yaml():
    """Test `to_yaml` method for simple class."""
    params_yaml = SIMPLE.to_yaml()
    assert params_yaml == SIMPLE_YAML


def test_simple_from_dict():
    """Test `from_dict` method for simple class."""
    params = Parameters.from_dict(dict(SIMPLE_ARGS))
    assert params.a == 2
    assert params.b == 0.0
    assert params.c == "abc"


def test_simple_from_yaml():
    """Test `from_yaml` method for simple class."""
    params = Parameters.from_yaml(SIMPLE_YAML)
    assert params.a == 2
    assert params.b == 0.0
    assert params.c == "abc"


@dataclass(slots=True)
class Inner(SlotsSerializer):
    value: int


@dataclass(slots=True)
class Outer(SlotsSerializer):
    inner: Inner


NESTED = Outer(Inner(10))


def test_nested_to_dict():
    """Test `to_dict` method for nested class."""
    nested_dict = NESTED.to_dict(recursive=False)
    assert "inner" in nested_dict
    assert isinstance(nested_dict["inner"], Inner)


def test_nested_to_dict_recursive():
    """Test `to_dict` method for nested class."""
    nested_dict = NESTED.to_dict(recursive=True)
    assert "inner" in nested_dict
    assert "value" in nested_dict["inner"]
    assert nested_dict["inner"]["value"] == 10


def test_nested_to_yaml():
    """Test `to_yaml` method for nested class."""
    nested_yaml = NESTED.to_yaml()
    assert nested_yaml == "inner:\n  value: 10\n"


def test_nested_from_dict():
    """Test `from_dict` method for nested class."""
    nested = Outer.from_dict({"inner": {"value": 10}})
    assert isinstance(nested, Outer)
    assert isinstance(nested.inner, Inner)
    assert isinstance(nested.inner.value, int)
    assert nested.inner.value == 10


def test_nested_from_yaml():
    """Test `from_yaml` method for nested class."""
    nested = Outer.from_yaml("inner:\n  value: 10\n")
    assert isinstance(nested, Outer)
    assert isinstance(nested.inner, Inner)
    assert isinstance(nested.inner.value, int)
    assert nested.inner.value == 10
