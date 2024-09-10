from typing import TypeVar

T = TypeVar("T")


def require_not_none(v: T, message: str) -> T:
    """
    Raise ValueError with message if v is not None, otherwise return v
    """
    if v is None:
        raise ValueError(message)
    return v


def first_not_none(*args: T | None) -> T:
    """
    :return: the first parameter that is not None
    :raises: ValueError if no parameter or all are None
    """
    for t in args:
        if t is not None:
            return t
    raise ValueError("At least one parameter must be not None")
