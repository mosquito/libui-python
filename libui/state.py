"""Reactive state containers for the declarative UI layer."""

from __future__ import annotations

from typing import Callable, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class State(Generic[T]):
    """Reactive container. Notifies subscribers on change.

    Usage::

        value = State(0)
        value.subscribe(lambda: print(value.value))
        value.value = 42  # prints 42
    """

    __slots__ = ("_value", "subscribers", "__updating")

    def __init__(self, initial: T) -> None:
        self._value = initial
        self.subscribers: set[Callable] = set()
        self.__updating = False

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new: T) -> None:
        self.set(new)

    def get(self) -> T:
        return self._value

    def set(self, new: T) -> None:
        if self.__updating or new == self._value:
            return
        self.__updating = True
        try:
            self._value = new
            for cb in set(self.subscribers):
                cb()
        finally:
            self.__updating = False

    def update(self, fn: Callable[[T], T]) -> None:
        """Apply a function to the current value: ``state.update(lambda x: x + 1)``."""
        self.set(fn(self._value))

    def subscribe(self, cb: Callable) -> Callable:
        """Add a subscriber. Returns an unsubscribe function."""
        self.subscribers.add(cb)
        return lambda: self.subscribers.discard(cb)

    def unsubscribe(self, cb: Callable) -> None:
        self.subscribers.discard(cb)

    def map(self, fn: Callable[[T], U]) -> Computed[U]:
        """Create a derived readonly state: ``greeting = name.map(lambda n: f'Hello {n}')``."""
        return Computed(self, fn)


class Computed(Generic[T]):
    """Readonly derived state. Updates automatically when source changes."""

    __slots__ = ("subscribers", "_source", "_fn", "_value")

    def __init__(self, source: State | Computed, fn: Callable) -> None:
        self._source = source
        self._fn = fn
        self._value = fn(source.get())
        self.subscribers: set[Callable] = set()
        source.subscribe(self._recompute)

    def _recompute(self) -> None:
        new = self._fn(self._source.get())
        if new == self._value:
            return
        self._value = new
        for cb in set(self.subscribers):
            cb()

    @property
    def value(self) -> T:
        return self._value

    def get(self) -> T:
        return self._value

    def subscribe(self, cb: Callable) -> Callable:
        self.subscribers.add(cb)
        return lambda: self.subscribers.discard(cb)

    def unsubscribe(self, cb: Callable) -> None:
        self.subscribers.discard(cb)

    def map(self, fn: Callable) -> Computed:
        return Computed(self, fn)


class ListState(Generic[T]):
    """Observable list for tables. Notifies on insert/delete/change."""
    __slots__ = ("data", "subscribers")

    def __init__(self, initial: list[T] | None = None) -> None:
        self.data: list[T] = list(initial) if initial else []
        self.subscribers: set[Callable] = set()

    def _notify(self, event: str, **kwargs) -> None:
        for cb in set(self.subscribers):
            cb(event, **kwargs)

    def subscribe(self, cb: Callable) -> Callable:
        self.subscribers.add(cb)
        return lambda: self.subscribers.discard(cb)

    def unsubscribe(self, cb: Callable) -> None:
        self.subscribers.discard(cb)

    def append(self, item: T) -> None:
        self.data.append(item)
        self._notify("inserted", index=len(self.data) - 1)

    def pop(self, index: int = -1) -> T:
        if index < 0:
            index = len(self.data) + index
        item = self.data.pop(index)
        self._notify("deleted", index=index)
        return item

    def __setitem__(self, index: int, value: T) -> None:
        self.data[index] = value
        self._notify("changed", index=index)

    def __getitem__(self, index: int) -> T:
        return self.data[index]

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self):
        return iter(self.data)
