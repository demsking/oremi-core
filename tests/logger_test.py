import logging
import logging.handlers
from unittest.mock import call, patch

from oremi.logger import Logger, OremiFormatter


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
  with patch('logging.StreamHandler') as mock_stream_handler, \
        patch('logging.handlers.RotatingFileHandler') as mock_file_handler:
    logger = Logger('test_logger')

  assert isinstance(logger, Logger)
  assert len(logger.handlers) == 2
  assert mock_stream_handler.called
  assert mock_file_handler.called

def test_logger_setglobal_level():
  Logger.setglobal_level(logging.INFO)
  assert Logger.global_level == logging.INFO

def test_logger_create():
  with patch('coloredlogs.install') as mock_coloredlogs:
    logger = Logger.create('test_logger')

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
