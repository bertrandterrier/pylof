from enum import Enum
from uuid import UUID
import re

from dataclasses import dataclass
from parser.symbols import Symbol
from parser.lexicon import Lexicon

class VRule(Enum):
    CLOSE = 0
    TURN = 1
    UNMARK_FLIP = 2
    MARK_FLIP = 3

class ReentryDir(Enum):
    LTR = 0
    RTL = 1

@dataclass
class StepCache:
    asc: list[UUID|tuple[bool, Symbol]]
    desc: list[ UUID | tuple[bool, Symbol] | ReentryDir ]
    base: str

class Escape(Enum):
    NULL = 0
    CHAR = 1
    BLOCK = 2
    SBLOCK = 3

class EOF(str):
    def __repr__(self) -> str:
        return "<EOF>"
    def __str__(self) -> str:
        return ""
    def __bool__(self) -> bool:
        return False

eof = EOF()
SPACE = " "


class StringCursor:
    def __init__(
        self,
        raw: str,
        esc_sign: str|None = None,
        esc_block: str|tuple[str, str]|None = None,
        auto_advance: bool = False,
    ):
        self._tokens: list[str] = list(raw) + [eof]
        self._pos: int = 0
        self.__virt_pos: int = 0

        self._parsed: list[str|Symbol|EOF] = []

        self._auto: bool = auto_advance
        self._esc_sign: str|None = esc_sign
        self._esc_block: str|tuple[str, str]|None = esc_block
        
    def __int__(self) -> int:
        return self._pos

    @property
    def tokens(self) -> list[str]:
        return self._tokens

    @property
    def auto(self) -> bool:
        return self._auto

    @property
    def esc_sign(self) -> str|None:
        return self._esc_sign

    @property
    def esc_block_start(self) -> str|None:
        if isinstance(self._esc_block, tuple):
            return self._esc_block[0]
        elif self._esc_block:
            return self._esc_block
        return

    @property
    def esc_block_stop(self) -> str|None:
        if isinstance(self._esc_block, tuple):
            return self._esc_block[-1]
        elif self._esc_block:
            return self._esc_block
        return

    def cursor(self, virt: bool):
        if virt:
            return self.__virt_pos
        return self._pos

    def add(self, sym: str|EOF|Symbol):
        if isinstance(sym, EOF):
            if self.result[-1] != eof:
                self._parsed.append(eof)
        else:
            self._parsed.append(sym)

    def peek_ahead(self, virt: bool) -> str|EOF:
        """Provides next Symbol or character, if available. Else EOF."""
        if self.cursor(virt) + 1 >= len(self.tokens):
            return eof
        return self.tokens[self.cursor(virt) + 1]

    def look_back(self, virt: bool) -> str|EOF:
        """Provides last Symbol or character, except if on position 0, then EOF."""
        if self.cursor(virt) < 0:
            return eof
        return self.tokens[self.cursor(virt)]

    def current(self, virt: bool) -> str|EOF:
        if self.cursor(virt) >= len(self.tokens):
            if not self._parsed[-1] == eof:
                self._parsed.append(eof)
            return eof
        return self.tokens[self.cursor(virt)]

    def advance(self, virt: bool):
        if virt:
            if self.__virt_pos < len(self.tokens) - 1:
                self.__virt_pos += 1
            return
        if self._pos < len(self.tokens) - 1:
            self._pos += 1
            self.__virt_pos = self._pos
            self._auto_advance()
        else:
            self.__virt_pos = self._pos
        return

    def _auto_advance(self):
        if not self.auto:
            return
        if self.current(False) == SPACE:
            return self.advance(False)
        elif self.current(False) == self.esc_sign:
            self.escape()
            return self._auto_advance()
        elif self.esc_block_start:
            if not self.rest(False).startswith(self.esc_block_start):
                self.escape()
                return self._auto_advance()

    def rest(self, virt: bool) -> str:
        return "".join(self.tokens[self.cursor(virt):])

    def escape(self, stop: str|None = None): 
        self.advance(True)
        if stop == None:
            self.add(self.current(True))
            self.advance(True)
            self.virt_cursor_pull()
            return

        cache: list[str] = []
        while self.current(True) != eof:
            if self.rest(True).startswith(stop):
                if len(cache) >= 1:
                    self.add("".join([str(s) for s in cache]))

                for _ in range(len(stop)):
                    self.advance(True)
                self.virt_cursor_pull()
                return
        raise SyntaxError("Escape block not closed...")

    def virt_cursor_pull(self):
        self._pos = self.__virt_pos

    def virt_reset(self):
        self.__virt_pos = self._pos

    def consume(self, rule: Symbol|str|None = None) -> int:
        if not rule:
            self._parsed.append(self.current(False))
            self.advance(False)
            return 1
        cache = self.current(False)
        while str(rule).startswith(cache):
            self.advance(True)
            char = self.current(True)

            if cache + char == str(rule):
                self.advance(True)
                self.virt_cursor_pull()
                self.add(rule)
                return 1
            if char == SPACE or isinstance(char, EOF):
                break
            else:
                cache += char
        self.virt_reset()
        return 0

    @property
    def result(self) -> list[Symbol|str|EOF]:
        return self._parsed

def parse_form(src: str, lex: Lexicon) -> list[Symbol|str|EOF]:
    cursor: StringCursor = StringCursor(src, auto_advance = True, esc_sign = "\\", esc_block = "/")


    while cursor.current(False) != eof:
        sym = lex.match(cursor.current(False))

        if sym.features == "sigil":
            if lex.match(cursor.peek_ahead(False)).symtype == SymType("mark", "turn")


        candidates: list[Symbol] = lex.filter(cursor.current(False))
        if len(candidates) <= 0:
            cursor.consume()
            continue
        candidates = sorted(candidates, key = len, reverse = True)

        success = 0
        for sym in candidates:
            success = cursor.consume(rule = sym)
            if success >= 1:
                break
        if success == 0:
            cursor.consume(None)

    return cursor.result
