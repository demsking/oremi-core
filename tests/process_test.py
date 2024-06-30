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
from unittest.mock import patch

from oremi_core.process import is_installed


def test_is_installed_installed():
  with patch('shutil.which', return_value='/usr/bin/library'):
    assert is_installed('library') is False

def test_is_installed_not_installed():
  with patch('shutil.which', return_value=None):
    assert is_installed('missing_library') is False

def test_is_installed_valid_path():
  with patch('shutil.which', return_value='/usr/bin/library'):
    with patch('os.path.exists', return_value=True):
      with patch('os.access', return_value=True):
        assert is_installed('library') is True

def test_is_installed_invalid_path():
  with patch('shutil.which', return_value='/usr/bin/library'):
    with patch('os.access', return_value=False):
      assert is_installed('library') is False
