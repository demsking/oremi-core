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

__all__ = [
  'flatten',
]


def flatten(items: list[list]):
  """
  Flattens a nested list of items into a single list.

  Args:
    items: A list of lists to be flattened.

  Returns:
    A flattened list.
  """
  flattened = []

  for item in items:
    if isinstance(item, list):
      flattened.extend(flatten(item))
    else:
      flattened.append(item)

  return flattened
