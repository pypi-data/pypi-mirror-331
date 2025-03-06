from enum import Enum
from typing import TypedDict, List, Dict, Union


JsonType = Union[
    None,
    int,
    float,
    str,
    bool,
    List['JsonType'],
    Dict[str, 'JsonType']
]


class BoolType(Enum):
    TRUE = 'true'
    FALSE = 'false'


class SettingsValueType(Enum):
    """Enum for the type of setting value."""
    STRING = 'str'
    INTEGER = 'int'
    FLOAT = 'float'
    BOOLEAN = 'bool'
    JSON = 'json'


ValueType = Union[
    str,
    int,
    float,
    BoolType,
    JsonType
]


class Settings(TypedDict):
    key: str
    value: ValueType
    type: SettingsValueType


BOOL_TYPE_TO_PYTHON_BOOL = {
    BoolType.TRUE: True,
    BoolType.FALSE: False
}
