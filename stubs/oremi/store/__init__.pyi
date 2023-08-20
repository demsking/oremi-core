from .decorators import Collection as Collection, MissingCollectionModelError as MissingCollectionModelError, MissingViewAnnotationError as MissingViewAnnotationError, MissingViewInitializationError as MissingViewInitializationError, MissingViewModelError as MissingViewModelError, Model as Model, Store as Store, View as View, store as store
from unqlite import UnQLite as UnQLite

def open_database(filename: str) -> UnQLite: ...
