# Round Trip INI Parser

For reading and respectfully modifying INI files when dealing with software that still uses this format.

This library aims to be as flexible as possible when it comes to interpreting `ini` files.

## Why roundtripini?

There are already a number of existing ini libraries, including python's builtin configparser, but not only do most of these libraries not support round-trip-parsing, most of them also do not support duplicate sections and keys.

roundtripini simultaneously supports round trip parsing, handling duplicate keys by treating them as lists, and allowing sections to be defined multiple times (with each section being queried when reading values).

## Why INI?

Lots of software still uses this poorly-specified format. roundtripini is designed to help interface with such software.

If you want a library to read configuration files for the software itself, I would recommend instead using a file format which has a specification and consistent implementations in multiple languages and for multiple platforms, like [TOML](https://toml.io) or [YAML](https://yaml.org).

## Usage

```python
from roundtripini import INI

with open("file") as file:
    ini = INI(file)

# Unlike configparser, ini takes a tuple, rather than returning a section when accessed with []
# This is necessary as multiple sections may exist in the file.
ini["section", "key"] = "value"
# Multiple values can be included as a list. Each one will be added with a separate key
ini["section", "key"] = ["value 1", "value 2"]
ini["section", "other key"] = "other value"
# When assigning values, single-element lists are equivalent to strings
ini["section", "other key"] = ["other value"]

assert ini.dump() == """[section]
key = value 1
key = value 2
other key = other value
"""

assert isinstance(ini["section", "key"], list)
assert isinstance(ini["section", "other key"], str)

with open("file", "w") as file:
    file.write(ini.dump())
```

## Restrictions

- key/value pairs must be separated by =
- keys may not begin or end with whitespace
- values will have beginning or ending whitespace stripped when returned.
- Comments will only be ignored if they are on one line, but not
    if they are on the same line as a key/value pair, where they will be treated as part of the value

## Implementation Notes
- Validation of key/value pairs occurs when data is used, not when the file is read.
- When replacing keys with duplicates, all old keys will be removed from all sections (in the
  case of duplicate sections),  and the new elements will be inserted in a single block at the
  location of the first old key.
- Lists returned by the `[]` operator should not be modified, as the underlying data will not change.
