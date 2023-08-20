import functools
from typing import Any, Generic, TypeVar
from collections.abc import Callable

import unqlite
from pydantic import BaseModel, PrivateAttr

__all__ = [
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

T = TypeVar('T')


class Model(Generic[T], BaseModel):
  _id: int = PrivateAttr(default = None)

  @classmethod
  def parse_record(cls, raw: dict) -> T:
    id = raw.pop('__id', None)
    ref: Any = cls.model_validate(raw)
    if id is not None:
      setattr(ref, '_id', id)
    return ref

  def __next__(self) -> T:
    ... # pragma: no cover


class Collection(Generic[T], unqlite.Collection):
  def all(self) -> list[T]: ...
  def append(self, record: T): ...
  def update(self, record: T): ...


class CollectionTable(unqlite.Collection):
  __model__: type[Model]

  def all(self):
    return [
      self.__model__.parse_record(item) for item in super().all()
    ]

  def append(self, record: Model):
    self.store(record.model_dump())

  def update(self, record: Model):
    super().update(record._id, record.model_dump())


class View(Generic[T]):
  def __init__(
    self,
    *,
    collection_name: str,
    filter_factory: Callable[[], Callable[[dict], bool]],
  ) -> None:
    self.collection_name = collection_name
    self.filter_factory = filter_factory

  def __len__(self) -> int:
    ... # pragma: no cover

  def __getitem__(self, index: int) -> T:
    ... # pragma: no cover

  def __iter__(self) -> T:
    ... # pragma: no cover


class MissingCollectionModelError(TypeError):
  pass


class MissingViewModelError(TypeError):
  pass


class MissingViewInitializationError(TypeError):
  pass


class MissingViewAnnotationError(TypeError):
  pass


def __configure_field(
  cls,
  defaults: dict[str, Any],
  models: dict[str, type[Model]],
  collections: list[str],
  computed: dict[str, View],
  field_name: str,
  field_type: Any,
) -> None:
  if field_name in cls.__dict__:
    if isinstance(cls.__dict__[field_name], (Collection, View)):
      computed[field_name] = cls.__dict__[field_name]
    else:
      defaults[field_name] = cls.__dict__[field_name]
  __configure_field_property(cls, models, collections, computed, field_name, field_type)


def __configure_field_property(
  cls,
  models: dict[str, type[Model]],
  collections: list[str],
  computed: dict[str, View],
  field_name: str,
  field_type: Any,
) -> None:
  if field_type.__name__ == Collection.__name__:
    if '__args__' in field_type.__dict__ and len(field_type.__dict__['__args__']) > 0:
      models[field_name] = field_type.__dict__['__args__'][0]
      collections.append(field_name)
    else:
      raise MissingCollectionModelError(f'Missing collection model for field {field_name}')
  elif field_type.__name__ == View.__name__:
    if '__args__' not in field_type.__dict__ or len(field_type.__dict__['__args__']) == 0:
      raise MissingViewModelError(f'Missing view model for field {field_name}')

    model_class: Model = field_type.__dict__['__args__'][0]
    setattr(model_class, '_id', None)

    if field_name in computed:
      field = computed[field_name]
      colname = f'__col_{field.collection_name}'
      filter_factory = field.filter_factory

      def view(self):
        collection = getattr(self, colname)
        items = collection.filter(filter_factory())
        return [model_class.parse_record(item) for item in items]
      setattr(cls, field_name, property(view))
    else:
      raise MissingViewInitializationError(f'Missing view initialization for field {field_name}')
  else:
    def getter(self):
      return self.__db.fetch(field_name).decode()
    def setter(self, value):
      self.__db.store(field_name, value)
    def deller(self):
      self.__db.delete(field_name)
    setattr(cls, field_name, property(getter, setter, deller))


DatabaseModelType = TypeVar('DatabaseModelType')


class Store:
  def commit(self):
    ... # pragma: no cover


M = TypeVar('M')


def store(cls: type[DatabaseModelType]) -> Callable[[unqlite.UnQLite], DatabaseModelType]:
  collections: list[str] = []
  defaults: dict[str, Any] = {}
  computed: dict[str, View] = {}
  models: dict[str, type[Model]] = {}

  for key, value in cls.__dict__.items():
    if isinstance(value, View) and key not in cls.__annotations__:
      raise MissingViewAnnotationError(f'Missing view annotation for field {key}')

  for field_name, field_type in cls.__annotations__.items():
    __configure_field(cls, defaults, models, collections, computed, field_name, field_type)

  def configure_collection(self, db: unqlite.UnQLite, colname: str) -> None:
    model_class = models[colname]
    collection: unqlite.Collection = CollectionTable(db, colname)
    collection.__model__ = model_class

    if not collection.exists():
      collection.create()
    setattr(self, f'__col_{colname}', collection)
    setattr(self, colname, collection)

  @functools.wraps(cls)
  def constructor(self: DatabaseModelType, db: unqlite.UnQLite) -> None:
    setattr(self, '__db', db)
    setattr(self, 'commit', lambda: db.commit())

    for colname in collections:
      configure_collection(self, db, colname)

    for field, value in defaults.items():
      if not db.exists(field):
        db.store(field, value)

  setattr(cls, '__init__', constructor)

  return cls
