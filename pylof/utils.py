from typing import Any, Callable, Container
from enum import Enum, EnumType

def eval_enum(val: int|str|Enum, enum: EnumType, use_enum_num: bool = False) -> Any:
    """Asserts enum even with enum and is case insensitive."""
    if isinstance(val, str):
        return enum(val.upper())
    elif isinstance(val, int):
        return enum(val)
    elif use_enum_num:
        return enum(val.value)
    else:
        return enum(val.name.upper())

def aslist(obj: Any) -> list:
    if isinstance(obj, list):
        return obj
    elif isinstance(obj, (tuple, set)):
        return [*obj]
    else:
        return [obj]

def search_lex(
    item: Any,
    lex: dict[str, Any],
    use_inner: str|list[str]|None = None,
    ignore_startswith: str|None = "_",
    func: Callable[[Any, Any], bool] = lambda x, L: x == L,
) -> list[str]:
    """Searches a (lexikon) dictionary for element. Lexikon dictionary can be nested.

    item: object
        Object searched for.
    lex: dict[str, str|dict]
        Lexikon with nested dictionaries.
    use_inner: str | list[str] | None
        To limit search scope. Keys from outest to innest limiter. Limiter will 
        not be returned.
    """
    use_lex: dict = {k: v for k,v in lex.items() if ignore_startswith and not k.startswith(ignore_startswith)}

    if use_inner:
        for key in aslist(use_inner):
            if not key in use_lex.keys():
                raise KeyError(f"Invalid key \"{key}\".")
            elif not isinstance(use_lex[key], dict):
                raise ValueError(f"Invalid type \"{type(use_lex)}\" for key \"{key}\". Expected dictionary.")
            use_lex = {k: v for k, v in use_inner}

    for key, val in use_lex.items():
        if isinstance(val, dict):
            inner_result: list[str] = search_lex(item, val, func = func)
            if inner_result:
                return [key] + inner_result
        elif func(item, val):
            return [key]
    return []

class HoldMode(Enum):
    ONLY = 3
    ALL = 2
    ONE = 1
    NONE = 0
    NOT_ALL = -1

def has(
    spec: Container,
    *args,
    mode: HoldMode|str = HoldMode.ALL
) -> bool:
    """Checks if a container holds an number of elements. Use mode to determine 
    behaviour."""
    if isinstance(mode, str):
        mode = HoldMode(mode.upper())

    count: int = 0
    for arg in args:
        if arg in spec:
            count += 1

    match mode.name:
        case 'ALL':
            return count == len(args)
        case 'NOT_ALL':
            return count < len(args)
        case 'ONLY':
            return count == len(args)
        case 'ONE':
            return count > 1
        case 'NONE':
            return count <= 0
