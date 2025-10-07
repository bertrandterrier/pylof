from dataclasses import dataclass
from enum import Enum

class EType(Enum):
    EMPTY = 0
    MRKCLS = 1
    MRKTRN = 2
    MRKSWITCH = 3
