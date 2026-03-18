"""Property decorator factories for coercing scraped values to int or float."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, overload


@overload
def int_property_decorator(func: Callable[..., Any]) -> property: ...


@overload
def int_property_decorator() -> Callable[[Callable[..., Any]], property]: ...


def int_property_decorator(
    func: Callable[..., Any] | None = None,
) -> property | Callable[[Callable[..., Any]], property]:
    """Decorate a property method to coerce its return value to ``int``.

    When applied to a property, the decorator wraps the underlying method so
    that its return value is converted to an ``int``.  If the conversion fails
    (e.g. the raw value is ``None`` or a non-numeric string) the property
    returns ``None`` instead of raising an exception.

    Can be used either as ``@int_property_decorator`` or as
    ``@int_property_decorator()`` (called with no arguments).

    Parameters
    ----------
    func : callable, optional
        The property function to wrap when the decorator is used without
        parentheses.

    Returns
    -------
    property or callable
        A ``property`` object when *func* is provided directly, otherwise a
        decorator callable that accepts the property function.

    """

    def decorator(inner: Callable[..., Any]) -> property:
        @property
        @wraps(inner)
        def wrapper(*args, **kwargs) -> int | None:
            value = inner(*args, **kwargs)
            try:
                return int(value)
            except (TypeError, ValueError):
                # If there is no value, default to None. None is statistically
                # different from 0 as a player/team who played an entire game and
                # contributed nothing is different from one who didn't play at all.
                # This enables flexibility for end-users to decide whether they
                # want to fill the empty value with any specific number (such as 0
                # or an average/median for the category) or keep it empty depending
                # on their use-case.
                return None

        return wrapper

    if func is None:
        return decorator

    return decorator(func)


@overload
def float_property_decorator(func: Callable[..., Any]) -> property: ...


@overload
def float_property_decorator() -> Callable[[Callable[..., Any]], property]: ...


def float_property_decorator(
    func: Callable[..., Any] | None = None,
) -> property | Callable[[Callable[..., Any]], property]:
    """Decorate a property method to coerce its return value to ``float``.

    When applied to a property, the decorator wraps the underlying method so
    that its return value is converted to a ``float``.  If the conversion fails
    (e.g. the raw value is ``None`` or a non-numeric string) the property
    returns ``None`` instead of raising an exception.

    Can be used either as ``@float_property_decorator`` or as
    ``@float_property_decorator()`` (called with no arguments).

    Parameters
    ----------
    func : callable, optional
        The property function to wrap when the decorator is used without
        parentheses.

    Returns
    -------
    property or callable
        A ``property`` object when *func* is provided directly, otherwise a
        decorator callable that accepts the property function.

    """

    def decorator(inner: Callable[..., Any]) -> property:
        @property
        @wraps(inner)
        def wrapper(*args, **kwargs) -> float | None:
            value = inner(*args, **kwargs)
            try:
                return float(value)
            except (TypeError, ValueError):
                # If there is no value, default to None. None is statistically
                # different from 0 as a player/team who played an entire game and
                # contributed nothing is different from one who didn't play at all.
                # This enables flexibility for end-users to decide whether they
                # want to fill the empty value with any specific number (such as 0
                # or an average/median for the category) or keep it empty depending
                # on their use-case.
                return None

        return wrapper

    if func is None:
        return decorator

    return decorator(func)
