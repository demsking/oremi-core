# Copyright 2023 Sébastien Demanou. All Rights Reserved.
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

import csv
import random
from typing import TypedDict

__all__ = [
  'Data',
  'split_data',
]

class Data(TypedDict):
  text: str
  label: str


def split_data(
  cvs_filename: str,
  delimiter = ',',
  test_size = 0.2,
  shuffle = True,
  header_label = 'label',
  header_text = 'text'
):
  """Split data from a CSV file into train and validation sets.

  This function reads data from a CSV file with the specified filename and splits it into train and validation sets.

  Args:
    cvs_filename (str): The filename of the CSV file to be read.
    delimiter (str): The delimiter used in the CSV file. Default is ','.
    test_size (float): The proportion of data to be used as validation data. Default is 0.2 (20%).
    shuffle (bool): Whether to shuffle the data before splitting. Default is True.
    header_label (str): The label for the header in the CSV file that contains the labels. Default is 'label'.
    header_text (str): The label for the header in the CSV file that contains the text data. Default is 'text'.

  Returns:
    labels (list): A list of labels extracted from the CSV file.
    train_data (list): A list of tuples containing the training data, where each tuple has two elements: the label and the text.
    validation_data (list): A list of tuples containing the validation data, where each tuple has two elements: the label and the text.
  """

  labels = []
  train_data = []
  validation_data = []

  with open(cvs_filename, encoding = 'utf-8') as file:
    reader = csv.reader(file, delimiter=delimiter)
    headers = [header.replace('\ufeff', '') for header in next(reader)]
    index_name = headers.index(header_label)
    index_text = headers.index(header_text)

    data_by_label = {}
    index_by_label = {}
    labels_items = []
    index = 0

    for index, line in enumerate(reader):
      label_name = line[index_name]
      label_code = index_by_label[label_name] if label_name in index_by_label else index
      text = line[index_text]

      if label_name not in data_by_label:
        index_by_label[label_name] = index
        index += 1

        data_by_label[label_name] = []
        labels_items.append({
          'code': label_code,
          'name': label_name,
        })

      data_by_label[label_name].append({
        'code': label_code,
        'label': label_name,
        'text': text,
      })

    for dataset in data_by_label.values():
      test_index = int(len(dataset) * test_size)

      if shuffle:
        random.shuffle(dataset)

      current_test_data = dataset[0:test_index]
      current_train_data = dataset[test_index:]

      train_data = [*train_data, *current_train_data]
      validation_data = [*validation_data, *current_test_data]

    labels_items.sort(key = lambda row: row['code'])
    labels = [label['name'] for label in labels_items]

  return labels, train_data, validation_data, data_by_label
