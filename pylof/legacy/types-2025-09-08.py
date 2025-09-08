from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Iterator, Literal, Protocol, runtime_checkable, ParamSpec

from pylof.utils import search_lex, has

P = ParamSpec("P")

class Char(str):
    def __new__(cls, token):
        if len(str(token)) != 1:
            raise SyntaxError(f"Invalid string length \"{len(token)}\". Expected single character.")
        return super().__new__(cls, token)

@runtime_checkable
class Stringable(Protocol):
    def __str__(self) -> str:
        ...

class MarkFeats(str):
    """A mark feature string is a string concatenation of mark features joined by 
    \".\".

    You can check if multiple marks are existing in a mark feat like
        `if ['feat1', 'feat2', ...] in mf`
    and it will be true in the case both features are contained in self.feats.

    Iterated will not be over characters, but over the feats.

    Concatenation is allowed for strings, list-likes and other MarkFeats instances. 
    String will be split to list, if \".\" is found. Returns a MarkFeats inscance 
    with added features.

    !!! dict behaviour is not determined for concatenation. Will be treated as simple iterable.

    Class is NOT case sensitive."""

    __slots__ = ("feats",)
    def __new__(cls, other):
        result: list[MarkFeats] = []
        if not other:
            inst = super().__new__(cls, "")
            inst.feats = []
            return inst
        elif isinstance(other, Iterable):
            for frag in other:
                result.append(cls(frag))
        elif isinstance(other, Stringable):
            result.append(MarkFeats(str(other).upper()))
        else:
            raise TypeError(f"Invalid type {type(other)}")
        inst = super().__new__(cls, ".".join(result).upper())
        inst.feats = result

        return inst

    def __contains__(self, other) -> bool:
        if isinstance(other, (MarkFeats, list, tuple)):
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
        if self == other or other in self:
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

    def __add__(self, other) -> "MarkFeats":
        new_feats = MarkFeats.concat_feats(self, other)
        return MarkFeats(new_feats)

    def __radd__(self, other) -> "MarkFeats":
        new_feats = MarkFeats.concat_feats(other, self)
        return MarkFeats(new_feats)

    def __iadd__(self, other):
        new_feats = MarkFeats.concat_feats(self, other)
        return MarkFeats(new_feats)

class StallMode(Enum):
    NULL = 0
    NUM = 1
    IDX = 2
    WORD = 3
    CMD = 3

class MarkOrder(Enum):
    NULL = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3

class MarkType(Enum):
    SPACE = 0
    MARK = 1
    OSCILLATOR = 2
    COUNTER = 3

class DescenderRule(Enum):
    NULL = 0
    LHALF = 1
    RHALF = 2
    FULL = 3

@dataclass
class Boundary:
    ascend: bool
    descend: DescenderRule
    sidereach: bool
    level: int

class Space:
    """The space is the space of the full form as well as the "spaces" inside of 
    expression created by the marks inside the form.

    Initializing a Space is creating an unfinished form. Use `self.mkform()` for 
    getting the finished form object, containing the graphical data for drawing 
    process for a form.
    
    For nesting spaces call the Space instance: `myspace(...)`.
    """
    __uids: list[int] = []

    _idx_chars: list[str] = [] 
    _cmd_chars: list[str] = []
    _mark_lex: dict = {}

    _func: Callable[..., list[str]]|None = None
    _func_params: tuple[list, dict] = ([], {})

    def __init__(
        self,
        char: Char | str,
        mark_lex: dict[Literal['mark', 'reentry'], dict],
        idx: str|None = None,
        idx_chars: list[str] = [],
        sigils: list[str] = ["-", ":"],
        mark_feat_search: Callable[P, list[str]] = search_lex,
        _parents: "list[Space]" = [],
        _children: "list[Space]" = [],
        *args,
        **kwargs,
    ):
        Space.__uids.append(len(self.__uids))
        self.__uid: int = self.__uids[-1]
        self.__run_state: StallMode|None = None
        self.__mark_state: MarkType = MarkType.SPACE

        self._idx: str|None = idx
        self._parents: list[Space] = [p for p in _parents]
        self._others: list[Space] = [c for c in _children]

        self._inv_scope: list[int] = []
        self._content: list = []
        self._sts: str = ""

        Space._func= mark_feat_search 
        Space._func_params= ([arg for arg in args], {k:v for k, v in kwargs.items()})

        if idx_chars:
            Space._idx_chars= [c for c in idx_chars]
        if mark_lex:
            Space._mark_lex= {k: v for k, v in mark_lex}
        if sigils:
            Space._cmd_chars= [s for s in sigils]


        if not self.__state and not self._parents:
            self._iscope = [0, 0]
            self.__state = StallMode.NULL

            # Behaviour only for the first initialization
            match char:
                case x if x.isnumeric():
                    self.__state = StallMode.NUM
                case x if x in Space._cmd_chars:
                    pass
                case " "|"\\":
                    pass
                case x if x in Space._idx_chars:
                    self.__state = StallMode.IDX
                case _:
                    mfs: MarkFeats = self.search(char)

                    if not mfs:
                        self._sts += char
                    elif mfs == 'close':
                        if mfs == 'reentry':
                            self.__mark_type = MarkType.COUNTER
                        elif mfs == 'mark':




    def mark(self) -> MarkType:
        return self.__mark

    @mark.setter
    def mark(self, other: int|str|MarkType|MarkOrder):
        self.__


    def step(self) -> tuple[int, int]:
        if not self._iscope:
            if not self._parents:
                raise RuntimeError("No parents")
            self._iscope = [*self.scope]
        else:
            self._iscope[1] = self._iscope[1] + 1
        return self.scope

    def set_real_scope(self, L: int, offset: int = 0) -> None:
        abs_length = L + offset
        inv_start, inv_stop = self.scope


    @property
    def uid(self) -> str:
        return f"F{self.__uid:09d}"

    @property
    def scope(self) -> tuple[int, int]:
        if not self._iscope and not self._parents:
            self._iscope = [0, -1]
        elif not self._iscope:
            for par in self._parents:
                self._iscope = [*par.scope]
        return self._iscope[0], self._iscope[1]

    @property
    def start(self) -> int:
        return self._iscope[0]

    @start.setter
    def start(self, other):
        if not isinstance(other, int):
            raise TypeError(f"Expected start positon of type integer, not of type \"{type(other)}\".")
        self._iscope[0]

    @property
    def nestlv(self) -> int:
        return len(self._parents)

    @classmethod
    def search(cls, char: str|Char) -> MarkFeats:
        if not cls._func:
            raise AssertionError("Missing search function...")
        result = cls._func(
            char,
            *cls._func_params[0],
            **cls._func_params[1]
        )
        return MarkFeats(result)



class Expression:

    def __init__(self, form: Space):
        self._form: list[]
