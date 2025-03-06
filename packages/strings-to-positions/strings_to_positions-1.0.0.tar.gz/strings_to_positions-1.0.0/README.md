# Strings to Positions

This library takes in the source text and a list of strings (or chunks) that occurs in the source text, the library will return either a list of offsets or a list of positions, the same length of the input list.

## How to Use

### Install

```sh
pip install strings-to-positions
```

### Usage Example

```py
from strings_to_positions import to_offsets, offset_to_position

# The Source Document
source_document = """# Introduction to Markdown

Markdown is a _lightweight **markup language** with plain-text_ formatting syntax. Its design allows it to be converted to many output formats, but the original tool by the same name only supports HTML.
Its design allows it to be converted to many output formats, but the original tool by the same name only supports HTML.

## Common Syntax
One common syntax is the one used by GitHub, which is a superset of the original Markdown syntax. It includes features such as tables, strikethrough, and task lists.
"""

# A list of strings, typically the output of a text splitter function
chunks = ["""# Introduction to Markdown

Markdown is a _lightweight **markup language** with plain-text_ formatting syntax. Its design allows it to be converted to many output formats, but the original tool by the same name only supports HTML.
Its design allows it to be converted to many output formats,""",
"""but the original tool by the same name only supports HTML.

## Common Syntax
One common syntax is the one used by GitHub, which is a superset of the original Markdown syntax. It includes features such as tables, strikethrough, and task lists.
"""
]

# Run the to_offsets function will output the offset positions of each chunk
offsets = to_offsets(source_document, chunks)
# offsets = [(0, 291), (292, 535)]

# Optionally you can set a third argument to configure the searching parameter.
# See below for details
# option = {
#   "case_sensitive": True, 
#   "allow_overlap": True, 
#   "overlap_size": None
# }
# offset = to_offsets(source_document, chunks, option)


# Run the offset_to_position in a loop will give you the list of positions
positionsList = []
for offset in offsets:
    if offset is None:
        positionsList.append(None)
        continue
    position = offset_to_position(document, offset)
    # position = {
    #    "start": {"line": 1, "column": 1, "offset": 0},
    #    "end": {"line": 4, "column": 61, "offset": 291},
    # }
    positionsList.append(position)

```

## Input Options
### `case_sensitive` (**True** | False)
If True, the function will consider casing during the search

### `allow_overlap` (**True** | False)
If True, the searching function will consider the entire previous chunk in sub document to be searched.
If `overlap_size` is set, then overlap will only consider the set size

### `overlap_size` (int | **None**)
Ignored if `allow_overlap` is False.  
Sets the size of the maximum overlap size

## Output Data Structure
### Offset

`Tuple[startOffset, endOffset]`

### Position

```
{
  start: {
    line: "1-index int",
    column: "1-index int",
    offset: int
  },
  end: {
    line: "1-index int",
    column: "1-index int",
    offset: int
  }
}
```
