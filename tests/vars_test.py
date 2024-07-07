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

import pytest

from oremi_core.vars import getenv


def setup_module(module):
  # Setting up environment variables for the tests
  os.environ['STRING_VAR'] = 'test_string'
  os.environ['INT_VAR'] = '123'
  os.environ['FLOAT_VAR'] = '123.456'
  os.environ['LIST_VAR'] = 'item1, item2, item3'
  os.environ['CHOICE_VAR'] = 'choice1'
  os.environ['EMPTY_VAR'] = ''


def teardown_module(module):
  # Clean up environment variables after tests
  del os.environ['STRING_VAR']
  del os.environ['INT_VAR']
  del os.environ['FLOAT_VAR']
  del os.environ['LIST_VAR']
  del os.environ['CHOICE_VAR']
  del os.environ['EMPTY_VAR']


def test_getenv_string():
  assert getenv('STRING_VAR') == 'test_string'
  assert getenv('MISSING_STRING_VAR', default='default_string') == 'default_string'
  with pytest.raises(OSError):
    getenv('MISSING_STRING_VAR')


def test_getenv_int():
  assert getenv('INT_VAR', expected_type=int) == 123
  assert getenv('MISSING_INT_VAR', default=456, expected_type=int) == 456
  with pytest.raises(TypeError):
    getenv('STRING_VAR', expected_type=int)
  with pytest.raises(TypeError):
    getenv('EMPTY_VAR', expected_type=int)


def test_getenv_float():
  assert getenv('FLOAT_VAR', expected_type=float) == 123.456
  assert getenv('MISSING_FLOAT_VAR', default=456.789, expected_type=float) == 456.789
  with pytest.raises(TypeError):
    getenv('STRING_VAR', expected_type=float)
  with pytest.raises(TypeError):
    getenv('EMPTY_VAR', expected_type=float)


def test_getenv_list():
  assert getenv('LIST_VAR', expected_type=list) == ['item1', 'item2', 'item3']
  assert getenv('MISSING_LIST_VAR', default='default1, default2', expected_type=list) == ['default1', 'default2']


def test_getenv_choices():
  assert getenv('CHOICE_VAR', choices=['choice1', 'choice2']) == 'choice1'
  with pytest.raises(ValueError):
    getenv('CHOICE_VAR', choices=['choice3', 'choice4'])
  with pytest.raises(ValueError):
    getenv('EMPTY_VAR', choices=['choice1', 'choice2'])


def test_getenv_empty_var():
  assert getenv('EMPTY_VAR', default='default_value') == ''
  assert getenv('EMPTY_VAR', default='default_value', expected_type=str) == ''
  assert getenv('EMPTY_VAR', default=['default'], expected_type=list) == []


def test_getenv_with_default_none():
  assert getenv('MISSING_VAR', default=None) is None
  assert getenv('MISSING_VAR', default=None, expected_type=str) is None
  assert getenv('MISSING_VAR', default=None, expected_type=list) is None
