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
