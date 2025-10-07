import json
from typing import Any

from pylof.datatypes import SymFeats,SymLex, Symbol 

def find_sym(scope: list[Symbol|Any], *feats, number: str|int|None = None) -> list[int]:
    """Returns index of a Symbol class element in a list."""
    result: list[int] = []
    for i, elem in enumerate(scope):
        if not isinstance(elem, Symbol):
            continue
        if not feats in elem.feats:
            if not [f.upper() for f in feats] in feats:
                continue
        if number and not number == elem.number:
            continue
        result.append(i)
    return result

def close_mark(cache: list[Symbol|Any], *feats, number: None|str|int = None) -> tuple[bool, list[Symbol|Any]]:
    raw = [s for s in cache]
    idx = find_sym(raw, *feats, number = number)
    if not idx:
        return False, raw
    del raw[idx[-1]]
    return True, raw

 
def parse_expression(src: str, lex: SymLex):
    """Parses form part of the pylof prompt."""

    parsed: list[Symbol|str] = []
    cache = ParsingCache()

    i = -1
    raw = list(src)
    while raw:
        char, i = (raw.pop(), i + 1)
        feats = SymFeats(lex(char))

        if feats == 'INDEX':
            cache.unassigned += char
        elif not feats:
            parsed.append(char)
            continue

        mark = Symbol(char + cache.unassigned, feats)
        cache.unassigned = ""

        if ['OPEN', 'MARKS'] == mark.feats:
            _, cache.opn_asc = close_mark(cache.opn_asc, 'MARK', 'CLOSE', number = mark.number)
        elif ['OPEN', 'RE-ENTRY'] == mark.feats:
            success = False
            for _type in ['COUNT', 'OSCILLATE']:
                success, cache.opn_asc = close_mark(cache.opn_asc, _type, number = mark.number)
                if success:
                    break
            if not success:
                raise ChildProcessError(f"RE-ENTRY OPEN: unclosable, {i}")
        elif 'CLOSE' in mark.feats:
            cache.opn_asc += [mark]
        elif 'OSCILLATE' in mark.feats:
            cache.opn_asc += [mark]
            cache.opn_desc += [mark]
        elif 'COUNT' in mark.feats:
            success = False
            for pos in ['asc', 'desc']:
                for _type in ['COUNTER', 'OSCILLATOR', 'RE-ENTER']:
                    success, new = close_mark(getattr(cache, f"opn_{pos}"), _type, number = mark.number)
                    if success:
                        setattr(cache, f"opn_{pos}", new)
                        if pos == 'asc':
                            cache.opn_desc.append(mark)
                        else:
                            cache.opn_asc.append(mark)
                        break
                if success:
                    break
            if not success:
                raise SyntaxError(
                    f"COUNT: unclosable, {i}"
                )
        elif "OSCILLATE-RE-ENTER" == mark.feats:
            success, cache.opn_desc = close_mark(cache.opn_desc, 'OSCILLATE-RE-ENTER', number = mark.number)
            if not success:
                raise SyntaxError(f"OSCILLATE-RE-ENTER: unclosable, {i}")
        elif "COUNT-RE-ENTER" == mark.feats:
            cache.opn_desc.append(mark)

        cache.asc = max(cache.asc, len(cache.opn_asc))
        cache.desc = max(cache.desc, len(cache.opn_desc))

        parsed.append(mark)

        print(f"""RUN #{i}
> max asc level: {str(cache.asc)}
> max desc level: {str(cache.desc)}
> unpaired marks, asc: {str(len(cache.opn_asc))}
> unpaired marks, desc: {str(len(cache.opn_desc))}
        """)
        print("MARKS:")
        for s in parsed:
            if isinstance(s, Symbol):
                print(f"> \"{s}\": {', '.join(s.feats)}")
    return

if __name__ == "__main__":
    print("!!! PYLOF PARSING TEST!!!\n")

    test = "<a><<b>c>"
    print(test)

    with open("pylof/docs/defaults.json", 'r') as f:
        d = json.load(f)

    lex = SymLex(d, func = lambda x, y: x == y or x in y)

    result = parse_expression(test, lex)
