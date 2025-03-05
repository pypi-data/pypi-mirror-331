from collections import Counter
from enum import Enum, auto
from json import dumps


class DetailLevel(Enum):
    BASIC = auto()
    ADVANCED = auto()


def create_counter(key_dictlist: dict) -> Counter:
    """Converts {key, dictlist} to Counter(key, len(dictlist))"""
    return Counter({key: len(dict_list) for key, dict_list in key_dictlist.items()})


def simple_text(value: str) -> str:
    return [{"text": value}]


def json_text(value, indent: int = None) -> str:
    return simple_text(dumps(obj=value, sort_keys=True, indent=indent))


def enumerate_any(map_or_sequence):
    return (
        map_or_sequence.items()
        if ObjectTypes.is_mapping_type(map_or_sequence)
        else enumerate(map_or_sequence)
    )


class ObjectTypes(Enum):
    SEQUENCE_TYPES = {"collapsed": "[...]", "types": (list, tuple, range)}
    MAPPING_TYPES = {"collapsed": "{...}", "types": (dict,)}
    SET_TYPES = {"collapsed": "[...]", "types": (set, frozenset)}
    RECURSIVE_TYPES = {
        "collapsed": "...",
        "types": SEQUENCE_TYPES["types"] + MAPPING_TYPES["types"] + SET_TYPES["types"],
    }

    def contains(self, obj) -> bool:
        return type(obj) in self.value["types"]

    def collapsed(self) -> str:
        return self.value["collapsed"]

    @staticmethod
    def is_mapping_type(obj) -> bool:
        return ObjectTypes.MAPPING_TYPES.contains(obj)

    @staticmethod
    def is_sequence_type(obj) -> bool:
        return ObjectTypes.SEQUENCE_TYPES.contains(obj)

    @staticmethod
    def is_recursive_type(obj) -> bool:
        return ObjectTypes.RECURSIVE_TYPES.contains(obj)
