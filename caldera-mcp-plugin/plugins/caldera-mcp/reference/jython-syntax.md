# Jython 2.7 Syntax Reference

Scripts run in Jython 2.7, not Python 3. Python 3 syntax causes SyntaxError at runtime.
Review every script against this list before running it.

## Contents
- String formatting
- Dict operations
- Prohibited syntax
- Integer division
- Module availability
- Exception handling
- Return values

## String Formatting

```python
# WRONG - SyntaxError in Jython 2.7
msg = f"Speed: {speed} RPM"

# RIGHT
msg = "Speed: {} RPM".format(speed)
msg = "Speed: %s RPM" % speed
```

## Dict Operations

```python
# WRONG - SyntaxError in Jython 2.7
combined = {**defaults, **overrides}

# RIGHT
combined = dict(defaults.items() + overrides.items())
```

## Prohibited Syntax

These Python 3+ features do not exist in Jython 2.7:

```python
# Walrus operator - does not exist
if (n := len(items)) > 10:  # SyntaxError
n = len(items)               # use assignment instead
if n > 10:

# Type hints - do not exist
def getStatus(path: str) -> dict:  # SyntaxError
def getStatus(path):                # omit type annotations

# Dataclasses - do not exist
# enum module - does not exist (use string constants)
# pathlib - does not exist
# typing - does not exist
```

## Integer Division

```python
# WRONG - returns 2 (integer division), not 2.5
result = 5 / 2

# RIGHT - force float division
result = 5.0 / 2
```

## Module Availability

Available: `collections.OrderedDict`, list/dict/set comprehensions, `json`, `re`, `sys`, `os`

Not available: `pathlib`, `typing`, `enum`, `dataclasses`, `f-strings`, `asyncio`

Java imports work: `from java.lang import String`, `from java.util import ArrayList`

## Exception Handling

```python
# Correct Jython 2.7 syntax
try:
    something()
except Exception as e:    # works in 2.7
    handle(e)

# For catching Java exceptions too, use bare except
try:
    java_call()
except:                    # catches both Python and Java exceptions
    handle_error()
```

The `except Exception as e:` form works but misses Java exceptions that don't extend Python's Exception class. Use bare `except:` when calling Java APIs where Java exceptions are possible.

## Return Values

The bridge captures the `_result` variable. This is the ONLY way to return structured data:

```python
# Assign your output to _result
_result = {
    "status": "ok",
    "data": processed_data
}
```

`print()` output goes to gateway logs but is not returned in the tool result.

Use `caldera:validate_script(code)` to syntax-check before running if unsure.
