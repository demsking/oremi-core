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
from oremi_core.array import flatten


def test_flatten_empty_list():
  input_list = []
  result = flatten(input_list)
  assert result == []

def test_flatten_single_list():
  input_list = [[1, 2, 3]]
  result = flatten(input_list)
  assert result == [1, 2, 3]

def test_flatten_multiple_lists():
  input_list = [[1, 2], [3, 4], [5, 6]]
  result = flatten(input_list)
  assert result == [1, 2, 3, 4, 5, 6]

def test_flatten_nested_lists():
  input_list = [[1, [2, 3]], [4, [5, 6, [7, 8]]]]
  result = flatten(input_list)
  assert result == [1, 2, 3, 4, 5, 6, 7, 8]

def test_flatten_mixed_lists():
  input_list = [[1, 2], [3, [4, 5]], [[6, 7], 8]]
  result = flatten(input_list)
  assert result == [1, 2, 3, 4, 5, 6, 7, 8]
