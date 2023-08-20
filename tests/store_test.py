from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

import pydantic
import pytest
from oremi.store import Collection
from oremi.store import MissingCollectionModelError
from oremi.store import MissingViewAnnotationError
from oremi.store import MissingViewInitializationError
from oremi.store import MissingViewModelError
from oremi.store import Model
from oremi.store import open_database
from oremi.store import Store
from oremi.store import store
from oremi.store import View
from oremi.store.decorators import CollectionTable

import unqlite


@patch('unqlite.UnQLite', autospec = True)
def test_open_database(mock_unqlite: Mock):
  open_database('/tmp/store.db')
  assert mock_unqlite.call_count == 1
  mock_unqlite.assert_has_calls([call('/tmp/store.db')])


def test_model_success():
  class UserModel(Model):
    username: str

  user = UserModel(username = 'chaka')

  assert isinstance(user.username, str)
  assert user.username == 'chaka'
  assert hasattr(user, '_id')
  assert getattr(user, '_id') is None


def test_model_failed():
  class UserModel(Model):
    username: str

  with pytest.raises(pydantic.ValidationError):
    UserModel(invalid_field = 'chaka') # type: ignore [reportGeneralTypeIssues]


def test_decorator_store_field_keyerror():
  @store
  class ServerStore(Store):
    host: str

  db = unqlite.UnQLite()
  server = ServerStore(db)

  with pytest.raises(KeyError):
    assert hasattr(server, 'host')


def test_decorator_store_field_manipulation():
  @store
  class ServerStore(Store):
    host: str

  db = unqlite.UnQLite()
  server = ServerStore(db)

  server.host = 'wakanda.ka'
  assert server.host == 'wakanda.ka'
  del server.host

  with pytest.raises(KeyError):
    assert server.host


def test_decorator_store_field_default():
  @store
  class ServerStore(Store):
    host: str = 'wakanda.ka'

  db = unqlite.UnQLite()
  server = ServerStore(db)

  assert hasattr(server, 'host')
  assert server.host == 'wakanda.ka'


def test_decorator_store_collection_missing_model():
  with pytest.raises(MissingCollectionModelError):
    @store
    class AccountsStore(Store):
      users: Collection


def test_decorator_store_with_collection_success():
  class UserModel(Model):
    username: str

  @store
  class AccountsStore(Store):
    users: Collection[UserModel]

  db = unqlite.UnQLite()
  accounts = AccountsStore(db)

  assert isinstance(accounts.users, CollectionTable)
  assert accounts.users.all() == []

  accounts.users.append(UserModel(username = 'chaka'))
  assert len(accounts.users) == 1 # type: ignore
  assert accounts.users.all()[0].username == 'chaka'
  assert accounts.users.all()[0]._id == 0

  user = accounts.users.all()[0]
  user.username += '2'

  accounts.users.update(user)
  assert len(accounts.users) == 1 # type: ignore
  assert accounts.users.all()[0].username == 'chaka2'


def test_store_view_missing_annotation():
  with pytest.raises(MissingViewAnnotationError):
    @store
    class AccountsStore(Store):
      active_users = View(
        collection_name = 'users',
        filter_factory = lambda: lambda record: record['active'],
      )


def test_store_view_missing_annotation_model():
  with pytest.raises(MissingViewModelError):
    @store
    class AccountsStore(Store):
      active_users: View


def test_store_view_missing_initialization():
  class UserModel(Model):
    username: str
    active: bool

  with pytest.raises(MissingViewInitializationError):
    @store
    class AccountsStore(Store):
      active_users: View[UserModel]


def test_store_view_success():
  class UserModel(Model):
    username: str
    active: bool

  @store
  class AccountsStore(Store):
    users: Collection[UserModel]
    active_users: View[UserModel] = View(
      collection_name = 'users',
      filter_factory = lambda: lambda record: record['active'],
    )

  db = unqlite.UnQLite()
  accounts = AccountsStore(db)

  accounts.users.store([
    { 'username': 'siya', 'active': False },
    { 'username': 'chaka', 'active': True },
  ])

  assert len(accounts.users.all()) == 2
  assert len(accounts.active_users) == 1
  assert accounts.active_users[0].username == 'chaka'
  assert accounts.active_users[0].active is True

  accounts.commit()
