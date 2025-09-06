from typing import Any, LiteralString
import re

def parse_expression(lines: list[str]|str, symbols: dict[str, str]) -> list[dict]:
    """Parses form part of the pylof prompt.""" 
