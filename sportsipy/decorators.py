from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Optional, overload


@overload
def int_property_decorator(func: Callable[..., Any]) -> property: ...


@overload
def int_property_decorator(
    func: None = None,
) -> Callable[[Callable[..., Any]], property]: ...


def int_property_decorator(func: Callable[..., Any] | None = None):
    def decorator(inner: Callable[..., Any]) -> property:
        @property
        @wraps(inner)
        def wrapper(*args) -> Optional[int]:
            value = inner(*args)
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
def float_property_decorator(
    func: None = None,
) -> Callable[[Callable[..., Any]], property]: ...


def float_property_decorator(func: Callable[..., Any] | None = None):
    def decorator(inner: Callable[..., Any]) -> property:
        @property
        @wraps(inner)
        def wrapper(*args) -> Optional[float]:
            value = inner(*args)
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
