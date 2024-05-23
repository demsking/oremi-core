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


def get_env_var(var_name: str, default_value=None):
  """
  Get the environment variable or return the default value if it is missing.
  If no default value is provided, raise an error if the variable is missing.

  Args:
    var_name (str): The name of the environment variable.
    default_value (str, optional): The default value to return if the environment variable is not found.

  Returns:
    str: The value of the environment variable or the default value if the variable is not found.

  Raises:
    EnvironmentError: If the environment variable is not found and no default value is provided.
  """
  value = os.getenv(var_name, default_value)
  if value is None:
    raise EnvironmentError(f"The environment variable '{var_name}' is missing and no default value is provided.")
  return value
