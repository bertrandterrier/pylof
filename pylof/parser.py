import json

from pylof.datatypes import SymFeats,SymLex, Symbol, ParsingCache

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

        if 'OPEN' in mark.feats:
            _type = ''
            if not 'MARK' in mark.feats:
                _type = 'REENTRY'

            found = False

            for level in ['top', 'bottom']:
                var = [m for m in getattr(cache, f"unpaired_{level}")]
                unpaired = []

                while var:
                    up_mark: Symbol = var.pop()
                    if not found:
                        if _type in up_mark.feats and mark.number == up_mark.number:
                            found = True
                            continue
                    unpaired = [up_mark] + unpaired

                if level == 'top':
                    cache.unpaired_top = unpaired
                else:
                    cache.unpaired_bottom = unpaired
                if found:
                    break

            if not found:
                raise SyntaxError(f"Could not match any unpaired mark for {mark}")
        elif 'CLOSE' in mark.feats:
            cache.unpaired_top += [mark]
            cache.ascending = max(cache.ascending, len(cache.unpaired_top))
        else:
            SyntaxError(f"Unexpected attributes for {mark}: {mark.feats}")
        parsed.append(mark)

        print(f"run #{i}")
        print("\nMAX ASCENDING:", str(cache.ascending))
        print("\nMAX DESCENDING:", str(cache.descending))
        print("LEFT UNPAIRED MARKS:", str(len(cache.unpaired_top) + len(cache.unpaired_bottom)))
        print("MARKS:")
        for s in parsed:
            if isinstance(s, Symbol):
                print(f"\t\"{s}\": {', '.join(s.feats)}")
    return

if __name__ == "__main__":
    print("!!! PYLOF PARSING TEST!!!\n")

    test = "<a><<b>c>"
    print(test)

    with open("pylof/docs/defaults.json", 'r') as f:
        d = json.load(f)

    lex = SymLex(d, func = lambda x, y: x == y or x in y)

    result = parse_expression(test, lex)
