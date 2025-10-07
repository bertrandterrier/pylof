from enum import Enum
import os
from typing import Iterator, Iterable, Literal, Union
from pathlib import Path

PathStr = Union[str, Path, os.PathLike]

class PairPosition(Enum):
    RIGHT_OFF = 1
    LEFT_OFF = 0
    INDIFFERENT = 2

class SymType(str):
    __slots__ = (
        "_feats",
        "_name",
    )
    def __new__(cls, *args: str):
        feats: list[str] = []
        for arg in args:
            if not arg.strip():
                continue
            elif '.' in arg:
                feats += [s.strip().lower() for s in arg.split(".") if len(s.strip()) > 0]
            else:
                feats.append(arg.strip().lower())
        inst = super().__new__(cls, ".".join(feats))
        inst._feats = feats
        inst._name = ".".join(feats)

        return inst

    @property
    def name(self) -> str:
        return self._name

    @property
    def features(self) -> list[str]:
        return [f for f in self._feats]


    def __contains__(self, other) -> bool:
        if isinstance(other, SymType):
            if len(other) > len(self):
                return False
            for f in other:
                if not f in self.features:
                    return False
            return True
        elif isinstance(other, Symbol):
            return self.__contains__(other.features)
        elif isinstance(other, str):
            if '.' in other:
                return self.__contains__(SymType(other))
            else:
                return other in self.features
        elif isinstance(other, (tuple, list)):
            for elem in other:
                if not elem in self.features:
                    return False
            return True
        return False

    def __iter__(self) -> Iterator:
        for feat in self.features:
            yield feat

    def __len__(self) -> int:
        return len(self.features)

    def __bool__(self) -> bool:
        return bool(self.features)

    def __eq__(self, other) -> bool:
        if isinstance(other, Symbol):
            return self.__eq__(other.features)
        elif isinstance(other, (tuple, list, SymType)):
            if len(self.features) != len(other):
                return False
            for f  in self.features:
                if not f in other:
                    return False
            return True
        elif isinstance(other, str):
            if len(self.features) <= 1:
                return self.__str__() == other.lower()
            elif '.' in other:
                return self.__eq__(SymType(other))
        return False

    @classmethod
    def concat_feats(cls, left, right) -> list[str]:
        new = []

        for side in [left, right]:
            if isinstance(side, str):
                if '.' in side:
                    new += [f for f in side.split(".")]
                else:
                    new += [side]
            elif isinstance(side, Iterable):
                new += [f for f in side]
            else:
                raise TypeError(f"Invalid type for concatenation {type(side)}")
        return new

    def __add__(self, other) -> "SymType":
        new_feats = SymType.concat_feats(self, other)
        return SymType(*new_feats)

    def __radd__(self, other) -> "SymType":
        new_feats = SymType.concat_feats(other, self)
        return SymType(*new_feats)

    def __iadd__(self, other):
        new_feats = SymType.concat_feats(self, other)
        return SymType(*new_feats)


class Symbol(str):
    __slots__ = (
        "_name",
        "_type",
        "_feats",
        "_spec",
        "_partners",
        "_sym",
    )
    def __new__(cls, sym: str|None, feats: list|SymType = [], spec: str|int|None = None):
        if isinstance(sym, Symbol):
            return sym
        if sym == None:
            inst = super().__new__(cls, "")
            inst._type = SymType("null")
            inst._sym = ""
            inst._feats = inst._type.features
            inst._name = inst._type.name
            inst._spec = None
            return inst
        inst = super().__new__(cls, sym)
        if isinstance(feats, list):
            feats = SymType(*feats)
        inst._type = feats
        inst._sym = sym
        inst._feats = inst._type.features
        inst._name = inst._type.name
        inst._spec = spec
        return inst

    def __eq__(self, other) -> bool:
        if isinstance(other, Symbol):
            return other.spec == self.spec and str(other) == str(self)
        return self.__str__() == other

    @property
    def spec(self) -> str|int:
        return self._spec or ""

    @property
    def features(self) -> list[str]:
        return self._feats

    @property
    def name(self) -> str:
        return self._name

    @property
    def symtype(self) -> SymType:
        return self._type

    @property
    def sym(self) -> str:
        return self._sym


def ismarktype(item: Symbol, *feats) -> bool:
    if not 'mark' in item.features and not 're-entry' in item.features:
        return False
    for f in feats:
        if not str(f).lower() in item.features:
            return False
    return True


def isoscillator(item) -> bool:
    if not ismarktype(item, 'second-order'):
        return False
    if ismarktype(item, 'counter'):
        return False
    return True


def iscounter(item) -> bool:
    if not ismarktype(item, 'second-order'):
        return False
    if ismarktype(item, 'oscillator'):
        return False
    return True

