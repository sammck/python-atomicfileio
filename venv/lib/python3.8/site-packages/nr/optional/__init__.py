
import typing as t

if t.TYPE_CHECKING:
  from nr.stream import Stream


__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '0.2.0'

T = t.TypeVar('T')
R = t.TypeVar('R')


class Optional(t.Generic[T]):

  def __init__(self, value: t.Optional[T]) -> None:
    self._value = value

  def __bool__(self) -> bool:
    return self._value is not None

  def get(self) -> T:
    if self._value is None:
      raise ValueError('Optional value is None')
    return self._value

  def or_else(self, fallback: R) -> t.Union[T, R]:
    if self._value is None:
      return fallback
    return self._value

  def or_else_get(self, f: t.Callable[[], R]) -> t.Union[T, R]:
    if self._value is None:
      return f()
    return self._value

  def or_throw(self, exc: t.Union[Exception, t.Callable[[], Exception]]) -> T:
    if self._value is None:
      if callable(exc):
        raise exc()
      else:
        raise exc
    return self._value

  def map(self, f: t.Callable[[T], t.Optional[R]]) -> 'Optional[R]':
    if self._value is None:
      return Optional(None)
    return Optional(f(self._value))

  def flatmap(self, f: t.Callable[[T], t.Iterable[R]]) -> 'Stream[R]':
    return self.stream().flatmap(f)

  def stream(self) -> 'Stream[T]':
    from nr.stream import Stream
    if self._value is None:
      return Stream()
    return Stream([self._value])
