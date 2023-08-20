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

import logging
import logging.handlers as handlers
import traceback
from typing import Any

import coloredlogs

__all__ = [
  'Logger',
  'OremiFormatter',
]


_format = '%(asctime)s - %(name)s - %(levelname)-s - %(message)s'

class OremiFormatter(logging.Formatter):
  def __init__(
    self,
    fmt: str = _format,
    datefmt: str = '%Y-%m-%d %H:%M:%S',
    style: str = '%',
    validate: bool = True,
  ) -> None:
    super().__init__(fmt, datefmt, style, validate) # type: ignore
    self.error_fmt = '%(asctime)s - %(name)s - %(levelname)-s - %(message)s'
    self.error_formatter = logging.Formatter(self.error_fmt, datefmt)

  def formatException(self, ei: Any) -> str:
    tb = ''.join(traceback.format_exception(*ei))
    last_line = tb.rstrip().split('\n')[-1]
    file_name, line_number, function_name, _ = traceback.extract_tb(ei[2])[-1]
    return f'{last_line} (File: {file_name}, Function: {function_name}, Line: {line_number})'


class Logger(logging.Logger):
  """
  Custom logger that extends the logging.Logger class.
  """
  global_level = logging.DEBUG

  def __init__(self, name: str, *, level: int | None = None, filename: str | None = None) -> None:
    super().__init__(name, level = level if isinstance(level, int) else Logger.global_level)

    formatter = OremiFormatter()
    console_handler = logging.StreamHandler()
    rotating_file_handler = handlers.RotatingFileHandler(
      filename = filename if filename else f'{name}.log',
      maxBytes = 10 * 1024 * 1024, # 10MB
      encoding = 'utf-8',
      backupCount = 100,
    )

    console_handler.setFormatter(formatter)
    rotating_file_handler.setFormatter(formatter)

    self.setLevel(Logger.global_level)
    self.addHandler(console_handler)
    self.addHandler(rotating_file_handler)

  @classmethod
  def set_global_level(cls, level: int) -> None:
    cls.global_level = level

  @classmethod
  def create(cls, name: str, level: int | None = None) -> 'Logger':
    """
    Creates a Trace logger instance with the specified name.

    Args:
      name (str): The name of the logger.
      level (int): The logger level.

    Returns:
      Logger: A Trace logger instance.
    """
    logger = cls(name, level = level)

    coloredlogs.install(
      logger = logger,
      fmt = _format,
      level = logger.level,
    )

    return logger

  def clone(self, name: str) -> 'Logger':
    """
    Clones the Trace logger with a new name.

    Args:
      name (str): The name of the cloned logger.

    Returns:
      Trace: A cloned Trace logger instance with the new name.
    """
    return Logger.create(f'{self.name} - {name}', self.level)
