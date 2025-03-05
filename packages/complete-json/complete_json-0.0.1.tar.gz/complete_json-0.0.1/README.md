# Complete JSON

A Python package that completes a JSON string if it has been truncated

Examples:

```python
from complete_json import complete_json

assert complete_json('{"a": 1') == '{"a": 1}'
assert complete_json('[{"one": {"a": 1') == '[{"one": {"a": 1}}]'
```

Supported python versions: `3.9` → `3.13`

## Links:

* [GitHub](https://github.com/mishaga/complete-json)
