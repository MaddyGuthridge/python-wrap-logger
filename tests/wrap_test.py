"""
Tests for the "wrappiness" of WrapLogger
"""
import pytest

from wrap_logger import wrap

from .helpers import Simple


def test_equal_properties():
    """Can we access internal properties of objects"""
    obj = Simple()
    wrapped = wrap(obj)

    assert wrapped.value == obj.value


def test_assign_properties():
    """Can we assign internal properties of objects"""
    obj = Simple()
    wrapped = wrap(obj)

    wrapped.value = 43

    # Both changed
    assert wrapped.value == obj.value
    assert wrapped.value == 43


def test_call_object():
    wrapped = wrap(Simple())
    assert wrapped(1, 2, a=3, b=4) == 10


def test_call_inner_function():
    """Can we call functions on objects"""
    obj = Simple()
    wrapped = wrap(obj)

    assert wrapped.echo('hi') == 'hi'


def test_non_existant_property_lookups_fail():
    """Do we get an error trying to access a property that doesn't exist"""
    with pytest.raises(AttributeError):
        # Access non-existent
        wrap(object()).invalid  # type: ignore  # noqa: B018


def test_wraps_modules():
    from . import example_module
    wrapped = wrap(example_module)

    assert wrapped.foo() == example_module.foo()
