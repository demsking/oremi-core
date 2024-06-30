# Copyright 2023-2024 Sébastien Demanou. All Rights Reserved.
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
import shutil

__all__ = [
  'is_installed',
]


def is_installed(lib_name: str) -> bool:
  """
  Check if a library or executable is installed.

  Args:
    lib_name (str): The name of the library or executable.

  Returns:
    bool: True if the library or executable is installed, False otherwise.
  """
  lib = shutil.which(lib_name)
  if lib is None:
    return False
  # else check if path is valid and has the correct access rights
  return os.path.exists(lib) and os.access(lib, os.X_OK)
