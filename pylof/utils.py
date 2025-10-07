from enum import Enum, EnumType
from typing import Any, Callable, Sequence
from warnings import warn

def to_enum(_type: EnumType, val: int|str|Enum, use_enum_num: bool = False) -> Any:
    """Asserts enum even with enum and is case insensitive."""
    if isinstance(val, str):
        return _type(val.upper())
    elif isinstance(val, int):
        return _type(val)
    elif use_enum_num:
        return _type(val.value)
    else:
        return _type(val.name.upper())

def aslist(obj: Any) -> list:
    if isinstance(obj, list):
        return obj
    elif isinstance(obj, (tuple, set)):
        return [*obj]
    else:
        return [obj]

def get_keychain(src: dict|list, item: Any, ignore: Callable[[str], bool] = lambda key: False) -> str|None:
    if isinstance(src, list):
        for i, elem in enumerate(src):
            if isinstance(elem, (dict, list)):
                result = get_keychain(elem, item, ignore)
                if result:
                    return f"{i}.{result}"
            elif elem == item:
                return str(i)

    for key, val in src:
        if ignore(key):
            continue
        if isinstance(val, (list, dict)):
            result = get_keychain(val, item, ignore)
            if result:
                return f"{key}.{result}"
        elif item == val:
            return str(key)
    return

def get_poss_keychains(src: dict|list, item: Any, ignore: Callable[[str], bool] = lambda key: False) -> list[str]:
    result: list[str] = []
    if isinstance(src, list):
        for i, elem in enumerate(src):
            if isinstance(elem, (dict, list)):
                inner_result = get_poss_keychains(elem, item, ignore)
                result += [f"{i}.{s}" for s in inner_result]
                continue
            if not isinstance(elem, str):
                warn(f"Not supported for type {type(elem)}")
                continue
            if elem.startswith(item):
                result.append(str(i))
    elif isinstance(src, dict):
        for key, val in src.items():
            if isinstance(val, (dict, list)):
                inner_result = get_poss_keychains(val, item, ignore)
                result += [f"{key}.{s}" for s in inner_result]
                continue
            if not isinstance(val, str):
                warn(f"Not supported for type {type(val)}")
            if val.startswith(item):
                result.append(val)
    return result


def bcheck(seq: Sequence, item: Any) -> bool:
    if len(seq) <= 0:
        return False
    return seq[-1] == item
