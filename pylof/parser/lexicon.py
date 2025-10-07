from typing import Any, Callable, Iterable
from pylof.parser.symbols import Symbol, SymType

class Lexicon:
    def __init__(
        self,
        *args: Symbol|tuple[str, ...],
    ):
        self._corpus: list[Symbol] = []
        self.update(*args)

    @property
    def corpus(self) -> list[Symbol]:
        return self._corpus

    def update(self, *args: Symbol|Iterable[str]):
        for arg in args:
            if isinstance(arg, Symbol):
                self._corpus.append(arg)
                continue
            if not isinstance(arg, tuple):
                arg = tuple(arg)
            char, feats = arg
            if not feats:
                raise ValueError(f"Features empty for character {char}")
            self._corpus.append(Symbol(char, SymType(*feats)))

    def get(self, key: str|SymType|list[str], default: Any = None) -> Symbol|Any:
        if isinstance(key, str):
            name = key
        elif isinstance(key, SymType):
            name = key.name
        else:
            name = SymType(*key).name

        for sym in self._corpus:
            if sym.name == name:
                return sym
        return default

    def match(self, chars: str) -> Symbol:
        """If not matching anything returns a NULL symbol."""
        for sym in self._corpus:
            if chars == str(sym):
                return sym
        return Symbol(None)

    def filter(self, chars: str, func: Callable[[str, Symbol], bool] = lambda x, y: str(y).startswith(x)) -> list[Symbol]:
        result: list[Symbol] = []
        for sym in self._corpus:
            if func(chars, sym):
                result.append(sym)
        return result

    def sublex(self, key: str) -> "Lexicon":
        result: list[Symbol] = []

        for sym in self._corpus:
            if key in sym.features:
                result.append(sym)
        return Lexicon(*result)



class LexBuilder:
    def __new__(cls, src: dict, **kwargs) -> Lexicon:
        symlist = cls.get_lex_entries(src, **kwargs)
        return Lexicon(*symlist)

    @classmethod
    def _get_elems_dict(cls, src: dict, ignorable: Callable[[str], bool]) -> tuple[list[str], list[str]]:
        names: list[str] = []
        syms: list[str] = []
        for key, val in src.items():
            if ignorable(key):
                continue
            elif isinstance(val, dict):
                inner_names, inner_syms = cls._get_elems_dict(val, ignorable)
                names += [f"{key}.{elem}" for elem in inner_names]
                syms += inner_syms
            elif isinstance(val, list):
                inner_names, inner_syms = cls._get_elems_list(val, ignorable)
                names += [f"{key}.{elem}" for elem in inner_names]
                syms += inner_syms
            else:
                names.append(key)
                syms.append(val)
        return names, syms

    @classmethod
    def _get_elems_list(cls, src: list, ignorable: Callable[[str], bool]) -> tuple[list[str], list[str]]:
        names, syms = ([], [])
        for count, elem in enumerate(src):
            if isinstance(elem, (list, dict)):
                inner_names, inner_syms = ([], [])
                if isinstance(elem, dict):
                    inner_names, inner_syms = cls._get_elems_dict(elem, ignorable)
                else:
                    inner_names, inner_syms = cls._get_elems_list(elem, ignorable)

                names += [f"{count};;{n}" for n in inner_names]
                syms += inner_syms

            else:
                names.append(str(count))
                syms.append(elem)
        return names, syms

    @classmethod
    def get_lex_entries(cls, src: dict, ignorable: Callable[[str], bool] = lambda key: False) -> list[Symbol]:
        names, syms = cls._get_elems_dict(src, ignorable)

        result: list[Symbol] = []

        for i, sym in enumerate(syms):
            _type = SymType(*names[i].split(";;"))
            result.append(Symbol(sym, _type))
        return result
