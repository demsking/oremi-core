__all__ = [
  'flatten',
]


def flatten(items: list[list]):
  """
  Flattens a nested list of items into a single list.

  Args:
    items: A list of lists to be flattened.

  Returns:
    A flattened list.
  """
  flattened = []

  for item in items:
    if isinstance(item, list):
      flattened.extend(flatten(item))
    else:
      flattened.append(item)

  return flattened
