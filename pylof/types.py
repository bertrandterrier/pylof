from typing import Literal, Protocol, runtime_checkable

@runtime_checkable
class Stringable(Protocol):
    def __str__(self) -> str:
        ...

class Symbol:
    __slots__ = (
        "body",
        "_alts",
    )
    def __eq__(self, other):
        if isinstance(other, Symbol):
            if other.body == self.body:
                return True
            for alt in self._alts:
                if alt == other.body:
                    return True
                for oalt in other._alts:
                    if oalt == alt:
                        return True
            return True
        if not isinstance(other, Stringable):
            return False
        var = str(other)
        if var == self.body:
            return True
        for alt in self._alts:
            if alt == var:
                return True
        return False

    def __new__(cls, token: Stringable, *alts) -> "Symbol":
        if not isinstance(token, str):
            token = str(token)

        inst = super().__new__(cls)
        inst.body = str(token)
        inst._alts = [e for e in alts]
        return inst

    def __add__(self, other) -> "Symbol":
        if isinstance(other, Symbol):
            self._alts += [e for e in other._alts]
            self._alts.append(other.body) 
        if not isinstance(other, Stringable):
            raise ArithmeticError(f"Cannot add type \"{type(other)}\".")
        self._alts.append(str(other))

        return self


class Pair(tuple):
    __slots__ = ("x", "y",)
    def __new__(
        cls,
        x: "Symbol|Stringable",
        y: "Symbol|Stringable|None",
    ) -> "Pair":
        if not isinstance(x, Symbol):
            var_x = Symbol(x)
        else:
            var_x = x
        if not y:
            var_y = var_x
        elif not isinstance(y, Symbol):
            var_y = Symbol(y)
        else:
            var_y = y

        inst = super().__new__(cls, [var_x, var_y])
        inst.x, inst.y = (var_x, var_y)

        return inst

    def __call__(self, other: Stringable):
        pass

