from enum import Enum
import json
import os
from pathlib import Path
import toml
from typing import Union

PathStr = Union[Path, os.PathLike, str]

class FType(Enum):
    JSON = 0
    TOML = 1
    LUA = 2

def load_conf_toml(path: PathStr, ftype: FType|int|str) -> dict:
    result: dict = {}

    if not isinstance(ftype, FType):
        ftype = FType(ftype)

    with open(path, "r") as f:
        match ftype.name:
            case "JSON":
                result = json.load(f)
            case "TOML":
                result = toml.load(f)
            case _:
                raise RuntimeError(f"{ftype.name} not yet supported.")
    return result

g_conf: dict = load_conf_toml(
    Path(__file__).parent.parent.joinpath("docs", "default.toml"),
    FType("TOML")
)
