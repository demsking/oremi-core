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
import random
from typing import Any

__all__ = [
  'flatten',
  'pick_item',
]


def flatten(items: list[Any]) -> list[Any]:
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


def pick_item(items: list[Any]) -> Any:
  """
  Pick a random item from a list of items.

  Args:
    items (list[Any]): A list of items.

  Returns:
    Any: A random item.
  """
  return random.sample(items, 1)[0]
