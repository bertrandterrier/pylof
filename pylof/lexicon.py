from dataclasses import dataclass
from typing import Any, Iterable, Union

StrArray = Union[str, Iterable[str]]

@dataclass
class MarkLex:
    open: StrArray
    close: StrArray

@dataclass
class ReentryLex:
    open: StrArray
    close: StrArray
    enter: StrArray
    flip: StrArray

@dataclass
class SymLex:
    mark: MarkLex 
    reentry: ReentryLex
    ireentry: ReentryLex
    re_enter: StrArray
    index: StrArray
    null: StrArray

DEF_MARKLEX: MarkLex = MarkLex(
    open = [ "<", "⟨" ],
    close = [ ">", "⟩" ]
)
DEF_REENTRY_LEX: ReentryLex = ReentryLex(
    open = "[",
    close = "]",
    enter = "-|",
    flip = "}"
)
DEF_REENTRY_RTL_LEX: ReentryLex = ReentryLex(
    open = "(",
    close = ")",
    enter = "|-",
    flip = "{"
)
DEF_SYMLEX = SymLex(
    mark = DEF_MARKLEX,
    reentry = DEF_REENTRY_LEX,
    ireentry = DEF_REENTRY_RTL_LEX,
    re_enter = "|",
    index = [ "*", "+", ":" ],
    null = [ ".", "_" ]
)
def Lex(dict):
    def __init__(self):
        ...
