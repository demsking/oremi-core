# Copyright 2023 Sébastien Demanou. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from datetime import datetime
from enum import Enum
from typing import Any, TypeVar, cast
from collections.abc import Callable

import dateutil.parser # pylint: disable=import-error

T = TypeVar('T')
EnumT = TypeVar('EnumT', bound=Enum)


def from_str(value: Any) -> str:
  assert isinstance(value, str)
  return value


def to_enum(class_type: type[EnumT], value: Any) -> EnumT:
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


def from_union(fs, values) -> Any:
  for fn in fs:
    try:
      return fn(values)
    except Exception:
      pass
  assert False


def to_float(value: Any) -> float:
  assert isinstance(value, float)
  return value


def to_class(class_type: type[T], value: Any) -> T:
  assert isinstance(value, class_type)
  return cast(Any, value).to_dict()


def from_datetime(value: Any) -> datetime:
  return dateutil.parser.parse(value)


def from_list(fn: Callable[[Any], T], value: Any) -> list[T]:
  assert isinstance(value, list)
  return [fn(y) for y in value]
