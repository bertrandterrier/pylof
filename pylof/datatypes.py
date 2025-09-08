from dataclasses import dataclass
from enum import Enum
import os
from typing import Callable, Iterator, Iterable, ParamSpec, Union
from pathlib import Path

from pylof.utils import search_lex

P = ParamSpec("P")

PathStr = Union[str, Path, os.PathLike]

class ConnectType(Enum):
    AWAITS = 0
    PROVIDES = 1
    DEMANDS = 2

class MarkState(Enum):
    MARKED = 1
    UNMARKED = 0

class VPos(Enum):
    DESCENDER = -1
    BASE =  0
    ASCENDER = 1

class SymFeats(str):
    __slots__ = ("feats",)
    def __new__(cls, *args: str|list):
        result: list[str] = []
        for arg in args:
            result.append(str(arg))
        inst = super().__new__(cls, ".".join(result).upper())
        inst.feats = result
        return inst

    def __contains__(self, other) -> bool:
        if isinstance(other, (SymFeats, list, tuple)):
            found = 0
            for elem in other:
                if elem in self.feats or str(elem).upper() in self.feats:
                    found += 1
            return found == len(other)
        elif isinstance(other, str):
            return other in str(self)
        return False

    def __iter__(self) -> Iterator:
        for feat in self.feats:
            yield feat

    def __len__(self) -> int:
        return len(self.feats)

    def __bool__(self) -> bool:
        return bool(self.feats)

    def __eq__(self, other) -> bool:
        if str(self) == other or other in self.feats:
            return True
        return False

    @classmethod
    def concat_feats(cls, left, right):
        new = []

        for side in [left, right]:
            if isinstance(side, str):
                if '.' in side:
                    new += [f.upper() for f in side.split(".")]
                else:
                    new += [side.upper()]
            elif isinstance(side, Iterable):
                new += [f for f in side]
            else:
                raise TypeError(f"Invalid type for concatenation {type(side)}")
        return new

    def __add__(self, other) -> "SymFeats":
        new_feats = SymFeats.concat_feats(self, other)
        return SymFeats(new_feats)

    def __radd__(self, other) -> "SymFeats":
        new_feats = SymFeats.concat_feats(other, self)
        return SymFeats(new_feats)

    def __iadd__(self, other):
        new_feats = SymFeats.concat_feats(self, other)
        return SymFeats(new_feats)

class Symbol(str):
    __slots__ = ("_feats", "_num",)
    def __new__(cls, sym: str, feats: list|SymFeats, number: str|int|None = None):
        inst = super().__new__(cls, sym)
        if isinstance(feats, list):
            feats = SymFeats(*feats)
        inst._feats = feats

        inst._num = number
        return inst

    def __eq__(self, other) -> bool:
        if isinstance(other, Symbol):
            return other.number == self.number and str(other) == str(self)
        elif isinstance(other, SymFeats):
            return self.feats in other
        return self.__str__() == other

    @property
    def number(self) -> str|int:
        return self._num or ""

    @property
    def feats(self) -> SymFeats:
        return self._feats

class SymLex:
    def __init__(
        self,
        lex: dict,
        _func: Callable[P, SymFeats|list[str]] = search_lex,
        *args,
        **kwargs
    ):
        self._lex: dict = {k:v for k,v in lex.items()}
        self._search_func: Callable[..., list[str]|SymFeats] = _func
        self._search_args: list = [x for x in args]
        self._search_kwargs: dict = {k: v for k, v in kwargs.items()}

    def __call__(self, key: str) -> SymFeats:
        result = self._search_func(key, self._lex, *self._search_args, **self._search_kwargs)
        if isinstance(result, SymFeats):
            return result
        elif isinstance(result, list):
            return SymFeats(result)
        raise TypeError(f"Invalid type {type(result)}")


@dataclass
class ParsingCache:
    unpaired_top: list[Symbol] = []
    unpaired_bottom: list[Symbol] = []
    ascending: int = 0
    descending: int = 0
    unassigned: str = ""

