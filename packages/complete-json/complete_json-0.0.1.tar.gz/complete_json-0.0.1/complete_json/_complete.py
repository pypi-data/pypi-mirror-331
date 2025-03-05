from types import MappingProxyType

OPEN_SQUARE = '['
CLOSE_SQUARE = ']'
OPEN_CURLY = '{'
CLOSE_CURLY = '}'
ESCAPE = '\\'
QUOTE = '"'

MAP = MappingProxyType(
    {
        QUOTE: QUOTE,
        OPEN_SQUARE: CLOSE_SQUARE,
        OPEN_CURLY: CLOSE_CURLY,
    }
)


def complete_json(input_json: str) -> str:
    stack = []

    for i, s in enumerate(input_json):
        if s == QUOTE:
            if i > 0 and input_json[i - 1] == ESCAPE:
                continue
            if stack and stack[-1] == QUOTE:
                stack.pop()
            else:
                stack.append(s)

        elif s in {OPEN_CURLY, OPEN_SQUARE}:
            stack.append(s)

        elif s in {CLOSE_CURLY, CLOSE_SQUARE}:
            last = stack[-1] if stack else ''
            if (s == CLOSE_CURLY and last == OPEN_CURLY) or (s == CLOSE_SQUARE and last == OPEN_SQUARE):
                stack.pop()
            else:
                ...
                # todo raise error / log a warning

    if not stack:
        return input_json

    # todo delete commas
    # todo delete escape

    regeneration = []

    while stack:
        last = stack.pop()
        regeneration.append(MAP[last])

    return '{original}{appendix}'.format(
        original=input_json,
        appendix=''.join(regeneration),
    )
