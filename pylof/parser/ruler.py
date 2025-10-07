from dataclasses import dataclass
from enum import Enum

from symbols import Symbol, SymType

class RuleType(Enum):
    ASC = 0
    VCLOSE = 10
    VTURN = 11
    VSWITCH = 12
    DESC = 20
    RLREENTRY = 21
    LLREENTRY =  22

class Link(Enum):
    NULL = 0
    VDOWN = 1
    VUP = 2
    HLDESC = 3
    HRDESC = 4
    HRASC = 5


@dataclass(frozen = True)
class FixedMarkRule:
    _uid: int
    _type: RuleType
    link: Link
    asc_offset: int = 0
    desc_offset: int = 0

class Rule:
    def __init__(self, uid: int, closer: Symbol|str, rtype: RuleType|int|str, next: Link):
        self.__uid: int = uid
        self._rtype: RuleType = RuleType(rtype)
        self._next: Link = Link(next)
        self._asc_offset: int = 0
        self._desc_offset: int = 0
        
        if isinstance(closer, Symbol):
            self._closer: Symbol = closer
        else:
            self._closer = Symbol(closer)

    @property
    def uid(self) -> int:
        return self.__uid

    @property
    def rtype(self) -> RuleType:
        return self._rtype

    @property
    def next(self) -> Link:
        return self._next

    @property
    def closer(self) -> Symbol:
        return self._closer

    def match(self, item: str|Symbol|SymType) -> bool:
        if not isinstance(item, Symbol) and self.closer.spec != "":
            return False
        elif isinstance(item, Symbol):
            return item == self.closer
        elif isinstance(item, SymType):
            return self.closer.symtype == item
        return self.closer.name == item
