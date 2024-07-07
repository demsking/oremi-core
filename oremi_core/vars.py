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
from typing import Any


def getenv(
  name: str,
  *,
  default: Any | None = None,
  expected_type: type = str,
) -> Any:
  """
  Get the environment variable or return the default value if it is missing.
  If no default value is provided, raise an error if the variable is missing.
  Optionally, validate the type of the environment variable's value.

  Args:
    name (str): The name of the environment variable.
    default (Any, optional): The default value to return if the environment variable is not found.
    expected_type (Type, optional): The expected type of the environment variable's value.

  Returns:
    Any: The value of the environment variable or the default value if the variable is not found.

  Raises:
    EnvironmentError: If the environment variable is not found and no default value is provided.
    TypeError: If the environment variable's value does not match the expected type.
  """
  value = os.getenv(name, default)

  if expected_type is str and not value and default is None:
    value = None

  if value is None:
    raise OSError(f"The environment variable '{name}' is missing and no default value is provided.")

  if expected_type is not None:
    try:
      value = expected_type(value)
    except (ValueError, TypeError):
      raise TypeError(f"The environment variable '{name}' should be of type {expected_type.__name__}.")

  return value
