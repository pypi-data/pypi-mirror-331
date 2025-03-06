import pytest


@pytest.fixture(scope="module")
def markdown_source():
    return """# Introduction to Markdown

Markdown is a _lightweight **markup language** with plain-text_ formatting syntax. Its design allows it to be converted to many output formats, but the original tool by the same name only supports HTML.
Its design allows it to be converted to many output formats, but the original tool by the same name only supports HTML.

## Common Syntax
One common syntax is the one used by GitHub, which is a superset of the original Markdown syntax. It includes features such as tables, strikethrough, and task lists.

### Code Syntax

By using backticks, you can create code blocks. For example, `const x = 5;`. You can [Google](https://google.com) youself.

You can also create code blocks.

```md
# Heading 1
## Heading 2
### Heading 3
```
"""


@pytest.fixture(scope="module")
def seq_chunk_1():
    return """# Introduction to Markdown

Markdown is a _lightweight **markup language** with plain-text_ formatting syntax. Its design allows it to be converted to many output formats, but the original tool by the same name only supports HTML.
Its design allows it to be converted to many output formats,"""


@pytest.fixture(scope="module")
def seq_chunk_2():
    return """but the original tool by the same name only supports HTML.

## Common Syntax
One common syntax is the one used by GitHub, which is a superset of the original Markdown syntax. It includes features such as tables, strikethrough, and task lists.
"""


@pytest.fixture(scope="module")
def seq_chunk_3():
    return """### Code Syntax

By using backticks, you can create code blocks. For example, `const x = 5;`. You can [Google](https://google.com) youself.

You can also create code blocks.

```md
# Heading 1
## Heading 2
### Heading 3
```"""


@pytest.fixture(scope="module")
def seq_offsets():
    return [(0, 291), (292, 535), (536, 759)]


@pytest.fixture(scope="module")
def overlap_chunk_1():
    return """# Introduction to Markdown

Markdown is a _lightweight **markup language** with plain-text_ formatting syntax. Its design allows it to be converted to many output formats, but the original tool by the same name only supports HTML.
Its design allows it to be converted to many output formats, but the original tool by the same name only supports HTML.

## Common Syntax"""


@pytest.fixture(scope="module")
def overlap_chunk_2():
    return """only supports HTML.

## Common Syntax
One common syntax is the one used by GitHub, which is a superset of the original Markdown syntax. It includes features such as tables, strikethrough, and task lists.

### Code Syntax

By using backticks,"""


@pytest.fixture(scope="module")
def overlap_chunk_3():
    return """ task lists.

### Code Syntax

By using backticks, you can create code blocks. For example, `const x = 5;`. You can [Google](https://google.com) youself.

You can also create code blocks.

```md"""


@pytest.fixture(scope="module")
def overlap_chunk_4():
    return """can [Google](https://google.com) youself.

You can also create code blocks.

```md
# Heading 1
## Heading 2
### Heading 3
```"""


@pytest.fixture(scope="module")
def overlap_chunks(overlap_chunk_1, overlap_chunk_2, overlap_chunk_3, overlap_chunk_4):
    return [overlap_chunk_1, overlap_chunk_2, overlap_chunk_3, overlap_chunk_4]


@pytest.fixture(scope="module")
def overlap_offsets():
    return [(0, 368), (331, 572), (522, 716), (634, 759)]

@pytest.fixture(scope="module")
def overlap_size_document():
    return """water water water water water water water water water water water
water water water water water water water water water water water water water water water water
water water water water water water water water water water
water water water water water water water water water water water water water water water water"""


@pytest.fixture(scope="module")
def overlap_size_chunks():
    return [
        "water water water water water water water",
        """water water water water water water
water water water water water water water """,
        """water water water water water water water water water water water""",
        """water water
water water water water water water water water water water""",
        """water water
water water water water water water water water water water water water water water water water""",
    ]


@pytest.fixture(scope="module")
def overlap_size_offsets():
    return [
        (0, 41),
        (30, 108),
        (96, 161),
        (150, 221),
        (210, 317),
    ]
