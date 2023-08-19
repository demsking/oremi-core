from datetime import datetime
from enum import Enum
from typing import Any, Callable, Type, TypeVar, cast

import dateutil.parser # pylint: disable=import-error

T = TypeVar('T')
EnumT = TypeVar('EnumT', bound=Enum)


def from_str(value: Any) -> str:
  assert isinstance(value, str)
  return value


def to_enum(class_type: Type[EnumT], value: Any) -> EnumT:
  assert isinstance(value, class_type)
  return value.value


def from_float(value: Any) -> float:
  assert isinstance(value, (float, int, str)) and not isinstance(value, bool)
  return float(value)


def from_int(value: Any) -> int:
  assert isinstance(value, (int, str)) and not isinstance(value, bool)
  return int(value)


def from_bool(value: Any) -> bool:
  assert isinstance(value, bool)
  return value


def from_none(value: Any) -> Any:
  assert value is None
  return value


def from_union(fs, values):
  for fn in fs:
    try:
      return fn(values)
    except Exception:
      pass
  assert False


def to_float(value: Any) -> float:
  assert isinstance(value, float)
  return value


def to_class(class_type: Type[T], value: Any) -> dict:
  assert isinstance(value, class_type)
  return cast(Any, value).to_dict()


def from_datetime(value: Any) -> datetime:
  return dateutil.parser.parse(value)


def from_list(fn: Callable[[Any], T], value: Any) -> list[T]:
  assert isinstance(value, list)
  return [fn(y) for y in value]
