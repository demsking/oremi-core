from oremi.array import flatten


def test_flatten_empty_list():
  input_list = []
  result = flatten(input_list)
  assert result == []

def test_flatten_single_list():
  input_list = [[1, 2, 3]]
  result = flatten(input_list)
  assert result == [1, 2, 3]

def test_flatten_multiple_lists():
  input_list = [[1, 2], [3, 4], [5, 6]]
  result = flatten(input_list)
  assert result == [1, 2, 3, 4, 5, 6]

def test_flatten_nested_lists():
  input_list = [[1, [2, 3]], [4, [5, 6, [7, 8]]]]
  result = flatten(input_list)
  assert result == [1, 2, 3, 4, 5, 6, 7, 8]

def test_flatten_mixed_lists():
  input_list = [[1, 2], [3, [4, 5]], [[6, 7], 8]]
  result = flatten(input_list)
  assert result == [1, 2, 3, 4, 5, 6, 7, 8]
