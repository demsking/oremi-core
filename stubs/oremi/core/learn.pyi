from typing import TypedDict

class Data(TypedDict):
    code: int
    text: str
    label: str

class CodeName(TypedDict):
    code: int
    name: str

def split_data(cvs_filename: str, delimiter: str = ..., test_size: float = ..., shuffle: bool = ..., header_label: str = ..., header_text: str = ...) -> tuple[list[str], list[Data], list[Data], dict[str, list[Data]]]: ...
