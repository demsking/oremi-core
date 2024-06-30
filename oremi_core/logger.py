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
import logging
import traceback
from logging import handlers
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
    last_line = tb.rstrip().rsplit('\n', maxsplit = 1000)[-1]
    file_name, line_number, function_name, _ = traceback.extract_tb(ei[2])[-1]
    return f'{last_line} (File: {file_name}, Function: {function_name}, Line: {line_number})'


class Logger(logging.Logger):
  """
  Custom logger that extends the logging.Logger class.
  """
  global_level = logging.DEBUG

  def __init__(self, name: str, *, level: int | None = None, filename: str | None = None) -> None:
    super().__init__(name, level = level or Logger.global_level)

    self.log_filename = filename

    formatter = OremiFormatter()
    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)
    self.addHandler(console_handler)

    if filename:
      rotating_file_handler = handlers.RotatingFileHandler(
        filename = filename if filename else f'{name}.log',
        maxBytes = 10 * 1024 * 1024, # 10MB
        encoding = 'utf-8',
        backupCount = 100,
      )

      rotating_file_handler.setFormatter(formatter)
      self.addHandler(rotating_file_handler)

  @classmethod
  def set_global_level(cls, level: int) -> None:
    cls.global_level = level

  @classmethod
  def create(cls, name: str, *, level: int | None = None, filename: str | None = None) -> 'Logger':
    """
    Creates a logger instance with the specified name.

    Args:
      name (str): The name of the logger.
      level (int): The logger level.
      filename (str): The name of the logger file.

    Returns:
      Logger: A logger instance.
    """
    logger = cls(name, level = level, filename = filename)

    coloredlogs.install(
      logger = logger,
      fmt = _format,
      level = logger.level,
    )

    return logger

  def clone(self, name: str) -> 'Logger':
    """
    Clones the logger with a new name.

    Args:
      name (str): The name of the cloned logger.

    Returns:
      Logger: A cloned logger instance with the new name.
    """
    return Logger.create(f'{self.name} - {name}', level = self.level, filename = self.log_filename)
