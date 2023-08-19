from unittest.mock import patch

from oremi.process import is_installed


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
