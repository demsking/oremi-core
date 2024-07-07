# Copyright 2024 Sébastien Demanou. All Rights Reserved.
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
import os
import uuid
from typing import Any

_NONE = uuid.uuid4()


def getenv(
  name: str,
  *,
  default: Any | None = _NONE,
  expected_type: type = str,
  choices: list[Any] | None = None,
) -> Any:
  """
  Get the environment variable or return the default value if it is missing.
  If no default value is provided, raise an error if the variable is missing.
  Optionally, validate the type of the environment variable's value and its
  value against a list of choices.

  Args:
    name (str): The name of the environment variable.
    default (Any, optional): The default value to return if the environment variable is not found.
    expected_type (Type, optional): The expected type of the environment variable's value.
    choices (list[Any], optional): A list of acceptable values for the environment variable.

  Returns:
    Any: The value of the environment variable or the default value if the variable is not found.

  Raises:
    OSError: If the environment variable is not found and no default value is provided.
    TypeError: If the environment variable's value does not match the expected type.
    ValueError: If the environment variable's value is not in the list of choices.
  """
  value = os.getenv(name, default)

  if value is _NONE:
    raise OSError(f"The environment variable '{name}' is missing and no default value is provided.")

  if expected_type is list:
    if isinstance(value, str):
      value = [item.strip() for item in value.split(',')]
    else:
      raise TypeError(
        f"The environment variable '{name}' should be a comma-separated string when expected_type is list. "
        f'Provided value: {value!r}.'
      )
  else:
    try:
      value = expected_type(value)
    except (ValueError, TypeError) as error:
      raise TypeError(
        f"The environment variable '{name}' should be of type '{expected_type.__name__}'. "
        f'Provided value: {value!r}.'
      ) from error

  if choices is not None and value not in choices:
    raise ValueError(
      f"The environment variable '{name}' has an invalid value. "
      f'Expected one of {choices}, but got {value!r}.'
    )

  return value
