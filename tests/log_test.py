"""
Tests for the "logginess" of WrapLogger
"""
import sys

import pytest
from jestspectation import Equals, StringContaining
from pytest import CaptureFixture

from wrap_logger import wrap

from .helpers import Simple


def test_capture_read(capsys: CaptureFixture[str]):
    """Are basic property accesses logged"""
    wrapped = wrap(Simple())
    _ = wrapped.value

    capture = capsys.readouterr()

    assert capture.out.strip() == '\n'.join([
        "[WRAP LOG] > Get  simple.value",
        "[WRAP LOG] < Get  simple.value: gave 42",
    ])


def test_capture_non_existent_read(capsys: CaptureFixture[str]):
    """Are exceptions logged for invalid reads"""
    wrapped = wrap(Simple())

    with pytest.raises(AttributeError):
        wrapped.invalid  # type: ignore  # noqa: B018

    capture = capsys.readouterr()
    assert capture.out.strip() == '\n'.join([
        "[WRAP LOG] > Get  simple.invalid",
        "[WRAP LOG] < Get  simple.invalid: raised "
        """AttributeError("'Simple' object has no attribute 'invalid'")""",
    ])


def test_capture_write(capsys: CaptureFixture[str]):
    """Are basic writes logged?"""
    wrapped = wrap(Simple())
    wrapped.value = 43

    capture = capsys.readouterr()
    assert capture.out.strip() == '\n'.join([
        "[WRAP LOG] > Set  simple.value: 42 -> 43",
        "[WRAP LOG] < Set  simple.value",
    ])


def test_capture_non_existent_write(capsys: CaptureFixture[str]):
    """Are basic writes logged for properties that didn't exist before?"""
    wrapped = wrap(Simple())
    wrapped.new = 43  # type: ignore

    capture = capsys.readouterr()
    assert capture.out.strip() == '\n'.join([
        "[WRAP LOG] > Set  simple.new: [unassigned] -> 43",
        "[WRAP LOG] < Set  simple.new",
    ])


def test_capture_call(capsys: CaptureFixture[str]):
    """Are object calls logged?"""
    wrapped = wrap(Simple())

    wrapped(1, 2, a=3, b=4)

    capture = capsys.readouterr()
    assert capture.out.strip() == '\n'.join([
        '[WRAP LOG] > Call simple(1, 2, a=3, b=4)',
        '[WRAP LOG] < Call simple(1, 2, a=3, b=4): returned 10',
    ])


def test_capture_call_method(capsys: CaptureFixture[str]):
    """Are object calls logged?"""
    wrapped = wrap(Simple())

    wrapped.echo("hi")

    capture = capsys.readouterr()
    assert capture.out.strip() == '\n'.join([
        "[WRAP LOG] > Get  simple.echo",
        "[WRAP LOG] < Get  simple.echo: gave "
        "<bound method Simple.echo of simple>",
        "[WRAP LOG] > Call simple.echo('hi')",
        "[WRAP LOG] < Call simple.echo('hi'): returned 'hi'",
    ])


def test_capture_module_function(capsys: CaptureFixture[str]):
    """Are function calls from wrapped modules logged?"""
    from . import example_module
    wrapped = wrap(example_module)

    _ = wrapped.foo()

    capture = capsys.readouterr()
    assert capture.out.strip().splitlines() == Equals([
        "[WRAP LOG] > Get  tests.example_module.foo",
        StringContaining(
            "[WRAP LOG] < Get  tests.example_module.foo: gave "
            "<function foo at 0x"
        ),
        "[WRAP LOG] > Call tests.example_module.foo()",
        "[WRAP LOG] < Call tests.example_module.foo(): returned 42",
    ])


def test_output_to_file_get(capsys: CaptureFixture[str]):
    """Are outputs written to the correct files for __getattr__?"""
    wrapped = wrap(Simple(), output=sys.stderr)
    _ = wrapped.value

    capture = capsys.readouterr()

    assert capture.err.strip() == '\n'.join([
        "[WRAP LOG] > Get  simple.value",
        "[WRAP LOG] < Get  simple.value: gave 42",
    ])


def test_output_to_file_set(capsys: CaptureFixture[str]):
    """Are outputs written to the correct files for __setattr__?"""
    wrapped = wrap(Simple(), output=sys.stderr)
    wrapped.value = 43

    capture = capsys.readouterr()
    assert capture.err.strip() == '\n'.join([
        "[WRAP LOG] > Set  simple.value: 42 -> 43",
        "[WRAP LOG] < Set  simple.value",
    ])


def test_output_to_file_call(capsys: CaptureFixture[str]):
    """Are outputs written to the correct files for __call__?"""
    wrapped = wrap(Simple(), output=sys.stderr)

    wrapped(1, 2, a=3, b=4)

    capture = capsys.readouterr()
    assert capture.err.strip() == '\n'.join([
        '[WRAP LOG] > Call simple(1, 2, a=3, b=4)',
        '[WRAP LOG] < Call simple(1, 2, a=3, b=4): returned 10',
    ])
