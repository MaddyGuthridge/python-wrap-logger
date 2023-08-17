
import sys
from typing import (
    Any,
    Optional,
    ParamSpec,
    TextIO,
    TypeVar,
    Generic,
    TYPE_CHECKING,
)
from itertools import chain


T = TypeVar('T')
P = ParamSpec('P')


def get_item_name(item: Any) -> str:
    try:
        return item.__name__
    except AttributeError:
        return repr(item)


# INVESTIGATE: Is using a generic here useful?
# Keeping it for the time being, but may remove if it's not helpful
class WrapLogger(Generic[T]):
    def __init__(
        self,
        subject: T,
        depth: int = 0,
        only_for_call: bool = False,
        name: Optional[str] = None,
        output: TextIO = sys.stdout,
    ) -> None:
        self.__name = name if name is not None else get_item_name(subject)
        self.__subject = subject
        self.__depth = depth
        self.__output = output
        self.__only_for_call = only_for_call

    def __getattr__(self, attr_name: str) -> Any:
        # Escape hatch for internal properties to prevent infinite recursion
        if attr_name.startswith(f"_{WrapLogger.__name__}__"):
            return super().__getattribute__(attr_name)

        # No logging if we're only tracking function calls
        if self.__only_for_call:
            return getattr(self.__subject, attr_name)

        full_name = f"{self.__name}.{attr_name}"
        print(f"[WRAP LOG] > Get  {full_name}")
        try:
            value = getattr(self.__subject, attr_name)
        except Exception as e:
            print(f"[WRAP LOG] < Get  {full_name}: raised {repr(e)}")
            raise
        print(f"[WRAP LOG] < Get  {full_name}: gave {repr(value)}")
        # For functions, add another layer of wrap log
        if callable(value):
            return WrapLogger(value, only_for_call=True, name=full_name)
        return value

    def __setattr__(self, attr_name: str, new_val: Any) -> None:
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
        print(f"[WRAP LOG] > Set  {full_name}: {og_val} -> {repr(new_val)}")
        setattr(self.__subject, attr_name, new_val)
        print(f"[WRAP LOG] < Set  {full_name}")

    def __call__(self, *args: tuple[Any, ], **kwargs: dict[str, Any]) -> Any:
        kwargs_strings = map(
            lambda pair: f"{pair[0]}={repr(pair[1])}",
            kwargs.items(),
        )
        args_string = ', '.join(chain(map(repr, args), kwargs_strings))

        call_sign = f"{self.__name}({args_string})"

        print(f"[WRAP LOG] > Call {call_sign}")
        # Ignore the mypy error, if this causes an exception, it's on the user
        # and mypy should have warned them regardless
        ret = self.__subject(*args, **kwargs)  # type: ignore
        print(f"[WRAP LOG] < Call {call_sign}: returned {repr(ret)}")
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


def wrap(subject: T) -> T:
    """
    Wrap an object so that its property accesses and method calls are logged
    """
    # Make tools like mypy and pylance still offer the original type checking
    # for user code
    if TYPE_CHECKING:
        return subject
    else:
        return WrapLogger(subject)