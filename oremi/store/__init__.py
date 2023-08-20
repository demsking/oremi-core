import unqlite
from unqlite import UnQLite

from .decorators import (
  Collection,
  MissingCollectionModelError,
  MissingViewAnnotationError,
  MissingViewInitializationError,
  MissingViewModelError,
  Model,
  Store,
  View,
  store,
)

__all__ = [
  'open_database',
  'Collection',
  'UnQLite',
  'Collection',
  'MissingCollectionModelError',
  'MissingViewAnnotationError',
  'MissingViewInitializationError',
  'MissingViewModelError',
  'Model',
  'Store',
  'View',
  'store',
]


def open_database(filename: str) -> UnQLite:
  """
  Open a database file and return an instance of UnQLite class.

  Args:
    filename (str): The name of the database file.

  Returns:
    UnQLite: An instance of UnQLite class connected to the specified database file.

  Example:
    # Open a database file named 'mydb.db' and get an instance of UnQLite class
    db = open_database('mydb.db')

    # Perform database operations using the db instance
    db.store('key1', 'value1')
    value = db.fetch('key1')
    db.delete('key1')
  """
  return unqlite.UnQLite(filename)
