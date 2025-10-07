from enum import Enum
from parser.symbols import Symbol


BARCHARS: dict[str, dict|str] = {
    'hbar': "―",
    'vbar': "│",
    'bottom-right': "┘",
    'bottom-left': "└",
    'top-right': "┐",
    'top-left': "┌"
}

class Escape(Enum):
    NULL = 0
    NEXT = 1
    BLOCK = 2
    SPECBLOCK = 3
