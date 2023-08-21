from typing import Any, Callable


class Collection:
  unqlite: 'UnQLite'
  name: str

  def __init__(self, db: 'UnQLite', name: str): ...

  def __len__(self):
    """Return the number of records in the document collection."""

  def exists(self) -> bool:
    """Check if the collection exists."""
    ... # pragma: no cover

  def create(self):
    """Create the collection."""
    ... # pragma: no cover

  def drop(self):
    """Drop (delete) the collection."""
    ... # pragma: no cover

  def store(self, record: dict | list[dict], *, return_id: bool = True) -> bool: # type: ignore [reportGeneralTypeIssues]
    """Store record in the collection.

    Args:
      records (dict | list[dict]): Dictionary representing the record to be stored or a list of dictionaries representing records to be stored.
      return_id (bool): Whether to return the ID of the inserted records. Default is True.

    Returns:
      bool: True if record is stored successfully, False otherwise.
    """
    ... # pragma: no cover

  def delete(self, record_id: int) -> bool:
    """Delete a record from the collection by its ID.

    Args:
      record_id (int): ID of the record to be deleted.

    Returns:
      bool: True if the record is deleted successfully, False otherwise.
    """
    ... # pragma: no cover

  def fetch(self, record_id: int) -> dict:
    """Fetch a record from the collection by its ID.

    Args:
      record_id (int): ID of the record to be fetched.

    Returns:
      dict: Dictionary representing the fetched record.
    """
    ... # pragma: no cover

  def update(self, record_id: int, record: dict) -> bool:
    """Update a record in the collection by its ID.

    Args:
      record_id (int): ID of the record to be updated.
      record (dict): Dictionary representing the updated record.

    Returns:
      bool: True if the record is updated successfully, False otherwise.
    """
    ... # pragma: no cover

  def iterator(self) -> Any:
    """Get an iterator for the collection.

    Returns:
      Any: Iterator for the collection.
    """
    ... # pragma: no cover

  def all(self) -> list[dict]:
    """Fetch all records in the collection.

    Returns:
      list[dict]: List of dictionaries representing all records in the collection.
    """
    ... # pragma: no cover

  def current_record_id(self) -> int:
    """Get the current record ID.

    Returns:
      int: Current record ID.
    """
    ... # pragma: no cover

  def last_record_id(self) -> int:
    """Get the ID of the last record in the collection.

    Returns:
      int: ID of the last record in the collection.
    """
    ... # pragma: no cover

  def reset_cursor(self):
    """Reset the cursor to the beginning of the collection."""
    ... # pragma: no cover

  def fetch_current(self):
    """Fetch the current record pointed by the cursor."""
    ... # pragma: no cover

  def creation_date(self):
    """Return the timestamp the collection was created (if exists) or None.

    Returns:
      Any: Timestamp of the collection creation or None if the collection does not exist.
    """
    ... # pragma: no cover

  def filter(self, filter: Callable[[dict], bool]) -> list[dict]:
    """Filter records in the collection

    Args:
      filter (Callable[[dict], bool]): Filter function that takes a dictionary representing a record as input and returns a boolean indicating whether the record should be included in the filtered result.

    Returns:
      list[dict]: List of dictionaries representing the records that pass the filter condition.
    """
    ... # pragma: no cover


UNQLITE_OPEN_READONLY = ...
UNQLITE_OPEN_READWRITE = ...
UNQLITE_OPEN_CREATE = ...
UNQLITE_OPEN_EXCLUSIVE = ...
UNQLITE_OPEN_TEMP_DB = ...
UNQLITE_OPEN_NOMUTEX = ...
UNQLITE_OPEN_OMIT_JOURNALING = ...
UNQLITE_OPEN_IN_MEMORY = ...
UNQLITE_OPEN_MMAP = ...

class UnQLite:
  filename: str

  def __init__(self, filename=':mem:', flags = UNQLITE_OPEN_CREATE, open_database=True, thread_safe=True): ...

  def open(self):
    """Open database connection."""

  def close(self):
    """Close database connection."""

  def __exit__(self, exc_type, exc_val, exc_tb): ...

  def __enter__(self):
    """Use database connection as a context manager."""

  def __setitem__(self, key, value): ...

  def __getitem__(self, key): ...

  def __delitem__(self, key): ...

  def __contains__(self, key): ...

  def __len__(self):
    """
    Return the total number of records in the database.

    Note: this operation is O(n) and requires iterating through the
    entire key-space.
    """

  def __next__(self): ...

  def collection(self, name: str) -> Collection:
    """Get a collection from the database by its name.
    See https://unqlite-python.readthedocs.io/en/latest/api.html

    Args:
      name (str): Name of the collection.

    Returns:
      Collection: Collection object representing the retrieved collection.
    """
    ... # pragma: no cover

  def store(self, key: str, value: str):
    """Store the given key-value pair in the database.

    Args:
      key (str): Key for the data.
      value (str): Value of the data.
    """
    ... # pragma: no cover

  def fetch(self, key: str) -> bytes:
    """Fetch the value associated with the given key from the database.

    Args:
      key (str): Key to fetch the value for.

    Returns:
      str: Value associated with the key.
    """
    ... # pragma: no cover

  def delete(self, key: str) -> None:
    """Delete the key-value pair associated with the given key from the database.

    Args:
      key (str): Key to delete.
    """
    ... # pragma: no cover

  def append(self, key: str, value: str) -> None:
    """Append the given value to the data stored in the key. If no data exists, the operation is equivalent to store().

    Args:
      key (str): Key to append the value to.
      value (str): Value to append to the existing data.
    """
    ... # pragma: no cover

  def exists(self, key: str) -> bool:
    """Check if the given key exists in the database.

    Args:
      key (str): Key to check for existence.

    Returns:
      bool: True if the key exists, False otherwise.
    """
    ... # pragma: no cover

  def begin(self):
    """Begin a transaction."""
    ... # pragma: no cover

  def rollback(self):
    """Rollback the current transaction."""
    ... # pragma: no cover

  def commit(self):
    """Commit the current transaction."""
    ... # pragma: no cover

  def transaction(self):
    """Context manager for handling transactions.

    Usage:
      with unqlite_db.transaction():
          # Transactional operations
    """
    ... # pragma: no cover

  def keys(self) -> list[str]:
    """A generator that successively yields the keys in the database"""
    ... # pragma: no cover

  def values(self) -> list[str]:
    """A generator that successively yields the values in the database."""
    ... # pragma: no cover

  def update(self, data: dict[str, str]) -> list[str]:
    """Update the database with the key-value pairs from the given dictionary. If any keys in data already exist, the values will be overwritten.

    Args:
      data (dict[str, str]): Dictionary containing the key-value pairs to update the database with.

    Returns:
      list[str]: List of keys that were updated.
    """
    ... # pragma: no cover

  def flush(self):
    """Delete all records in the database."""
    ... # pragma: no cover

  def random_string(self, size: bytes) -> str:
    """Generate a random string of the given size in bytes.

    Args:
      size (bytes): Size of the random string.

    Returns:
      str: Random string of the given size.
    """
    ... # pragma: no cover

  def random_number(self) -> int:
    """Generate a random integer number.

    Returns:
      int: Random integer number.
    """
    ... # pragma: no cover

  def disable_autocommit(self):
    """When the database is closed, prevent any uncommitted writes from being saved."""
    ... # pragma: no cover
