"""
# Wrap Logger

A library to wrap around objects and modules in Python and log property
accesses and calls.

This file contains the under-the-hood implementation of the tool.

## MIT License

Copyright (c) 2023 Maddy Guthridge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Some environments where wrap-logger needs to run don't include the typing
# module, so silence any import errors to make it work there
try:
    from typing import (
        Any,
        Optional,
        TextIO,
        TypeVar,
        TYPE_CHECKING,
    )
    from typing_extensions import ParamSpec
except ImportError:
    TYPE_CHECKING = False  # type: ignore
    pass

from itertools import chain


if TYPE_CHECKING:
    T = TypeVar('T')
    P = ParamSpec('P')


def get_item_name(item: 'Any') -> str:
    try:
        return item.__name__
    except AttributeError:
        return repr(item)


class WrapLogger:
    """
    Wrapper class. Wraps around objects to provide the logging functionality.
    """
    def __init__(
        self,
        subject: 'Any',
        depth: int = 0,
        only_for_call: bool = False,
        name: 'Optional[str]' = None,
        output: 'Optional[TextIO]' = None,
    ) -> None:
        self.__name = name if name is not None else get_item_name(subject)
        self.__subject = subject
        # TODO: Use this
        self.__depth = depth
        self.__output = output
        self.__only_for_call = only_for_call

    def __getattr__(self, attr_name: str) -> 'Any':
        # Escape hatch for internal properties to prevent infinite recursion
        if attr_name.startswith(f"_{WrapLogger.__name__}__"):
            return super().__getattribute__(attr_name)

        # No logging if we're only tracking function calls
        if self.__only_for_call:
            return getattr(self.__subject, attr_name)

        full_name = f"{self.__name}.{attr_name}"
        print(f"[WRAP LOG] > Get  {full_name}", file=self.__output)
        try:
            value = getattr(self.__subject, attr_name)
        except Exception as e:
            print(
                f"[WRAP LOG] < Get  {full_name}: raised {repr(e)}",
                file=self.__output,
            )
            raise
        print(
            f"[WRAP LOG] < Get  {full_name}: gave {repr(value)}",
            file=self.__output,
        )
        # For functions, add another layer of wrap log
        if callable(value):
            return WrapLogger(value, only_for_call=True, name=full_name)
        return value

    def __setattr__(self, attr_name: str, new_val: 'Any') -> None:
        # Escape hatch for internal properties to prevent setting internal
        # properties on the subject class
        if attr_name.startswith(f"_{WrapLogger.__name__}__"):
            return super().__setattr__(attr_name, new_val)

        # No logging if we're only tracking function calls
        if self.__only_for_call:
            setattr(self.__subject, attr_name, new_val)

        full_name = f"{self.__name}.{attr_name}"
        try:
            og_val = repr(getattr(self.__subject, attr_name))
        except AttributeError:
            og_val = "[unassigned]"
        print(
            f"[WRAP LOG] > Set  {full_name}: {og_val} -> {repr(new_val)}",
            file=self.__output,
        )
        setattr(self.__subject, attr_name, new_val)
        print(f"[WRAP LOG] < Set  {full_name}", file=self.__output)

    def __call__(
        self,
        *args: 'Any',
        **kwargs: 'Any',
    ) -> 'Any':
        kwargs_strings = map(
            lambda pair: f"{pair[0]}={repr(pair[1])}",
            kwargs.items(),
        )
        args_string = ', '.join(chain(map(repr, args), kwargs_strings))

        call_sign = f"{self.__name}({args_string})"

        print(f"[WRAP LOG] > Call {call_sign}", file=self.__output)
        # Ignore the mypy error, if this causes an exception, it's on the user
        # and mypy should have warned them regardless
        ret = self.__subject(*args, **kwargs)  # type: ignore
        print(
            f"[WRAP LOG] < Call {call_sign}: returned {repr(ret)}",
            file=self.__output,
        )
        return ret

    @property
    def __class__(self) -> type:
        # Override __class__ property to pretend to be an instance of the class
        # we are wrapping
        # https://stackoverflow.com/questions/52168971/instancecheck-overwrite-shows-no-effect-what-am-i-doing-wrong
        # Although this is dubious, it works, and the behaviour seems to be
        # relied on by the standard library, so it is unlikely to break
        # https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.__class__
        return self.__subject.__class__

    @__class__.setter
    # Error: redefinition of unused '__class__' from line 86
    # TODO: is this a bug in flake8?
    def __class__(self, new_class: type) -> None:  # noqa: F811
        self.__subject.__class__ = new_class


def wrap(subject: 'T', output: 'Optional[TextIO]' = None) -> 'T':
    """
    Wrap an object so that its property accesses and method calls are logged

    Args:
        subject (T): object to wrap
        output (Optional[TextIO], optional): output file to write to. Defaults
            to None for stdout.

    Returns:
        T: the wrapped object
    """
    # Make tools like mypy and pylance still offer the original type checking
    # for user code
    if TYPE_CHECKING:
        return subject
    else:
        return WrapLogger(subject, output=output)
