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
import logging.handlers
from unittest.mock import call
from unittest.mock import patch

from oremi_core.logger import Logger
from oremi_core.logger import OremiFormatter


def test_oremi_formatter_formatting():
  formatter = OremiFormatter()
  record = logging.LogRecord(
    name='test_logger',
    level=logging.INFO,
    pathname='test_file.py',
    lineno=42,
    msg='Test message',
    args=(),
    exc_info=None
  )

  result = formatter.format(record)

  expected_output = f'{record.asctime} - {record.name} - {logging.getLevelName(record.levelno)} - {record.msg}' # pylint: disable=no-member
  assert result == expected_output


def test_oremi_formatter_format_exception():
  formatter = OremiFormatter()
  exception_info = (ValueError, ValueError('Test Exception'), None)

  expected_output = 'ValueError: Test Exception (File: test_file.py, Function: test_function, Line: 42)'
  with patch('traceback.extract_tb', return_value=[('test_file.py', 42, 'test_function', 'code')]):
    result = formatter.formatException(exception_info)

  assert result == expected_output

def test_logger_constructor():
  with patch('logging.StreamHandler') as mock_stream_handler:
    logger = Logger('test_logger')

  assert isinstance(logger, Logger)
  assert len(logger.handlers) == 1
  assert mock_stream_handler.called

def test_logger_constructor_with_filename():
  with patch('logging.StreamHandler') as mock_stream_handler, \
        patch('logging.handlers.RotatingFileHandler') as mock_file_handler:
    logger = Logger('test_logger', filename = 'app.log')

  assert isinstance(logger, Logger)
  assert len(logger.handlers) == 2
  assert mock_stream_handler.called
  assert mock_file_handler.called

def test_logger_set_global_level():
  Logger.set_global_level(logging.INFO)
  assert Logger.global_level == logging.INFO

def test_logger_create_without_filename():
  with patch('coloredlogs.install') as mock_coloredlogs:
    logger = Logger.create('test_logger')

  assert isinstance(logger, Logger)
  assert mock_coloredlogs.called

  expected_coloredlogs_calls = [
    call(logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)-s - %(message)s', level=Logger.global_level)
  ]
  mock_coloredlogs.assert_has_calls(expected_coloredlogs_calls)

def test_logger_create():
  with patch('coloredlogs.install') as mock_coloredlogs:
    logger = Logger.create('test_logger')

  assert isinstance(logger, Logger)
  assert len(logger.handlers) == 1
  assert mock_coloredlogs.called

  expected_coloredlogs_calls = [
    call(logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)-s - %(message)s', level=Logger.global_level)
  ]
  mock_coloredlogs.assert_has_calls(expected_coloredlogs_calls)

def test_logger_create_with_filename():
  with patch('coloredlogs.install') as mock_coloredlogs:
    logger = Logger.create('test_logger', filename = 'app.log')

  assert isinstance(logger, Logger)
  assert len(logger.handlers) == 2
  assert mock_coloredlogs.called

  expected_coloredlogs_calls = [
    call(logger=logger, fmt='%(asctime)s - %(name)s - %(levelname)-s - %(message)s', level=Logger.global_level)
  ]
  mock_coloredlogs.assert_has_calls(expected_coloredlogs_calls)

def test_logger_full_usage():
  with patch('logging.StreamHandler') as mock_stream_handler, \
        patch('logging.handlers.RotatingFileHandler') as mock_file_handler:
    logger = Logger('test_logger', filename='test.log')

  assert isinstance(logger, Logger)
  assert len(logger.handlers) == 2
  assert mock_stream_handler.called
  assert mock_file_handler.called

  expected_calls = [
    call(filename='test.log', maxBytes=10485760, encoding='utf-8', backupCount=100)
  ]
  mock_file_handler.assert_has_calls(expected_calls)

# def test_logger_create_with_level():
#   with patch('coloredlogs.install') as mock_coloredlogs:
#     logger = Logger.create('test_logger_with_level', level=logging.CRITICAL)

#   assert isinstance(logger, Logger)
#   assert logger.level == logging.CRITICAL
#   assert mock_coloredlogs.called

def test_logger_clone():
  original_logger = Logger.create('original_logger', level=logging.DEBUG)
  with patch('coloredlogs.install') as mock_coloredlogs:
    cloned_logger = original_logger.clone('cloned_logger')

  assert cloned_logger.name == 'original_logger - cloned_logger'
  # assert cloned_logger.level == logging.DEBUG

  assert mock_coloredlogs.called
