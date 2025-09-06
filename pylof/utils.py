from typing import Any, Pattern, LiteralString
import re

def aslist(obj: Any) -> Any:
    if isinstance(obj, list):
        return obj
    elif isinstance(obj, (tuple, set)):
        return [*obj]
    else:
        return [obj]
