import pytest
from strings_to_positions import to_offsets  # import the package to test


@pytest.mark.parametrize(
    "source_text, chunks, options, expected",
    [
        ("abc", ["a", "b", "c"], None, [(0, 1), (1, 2), (2, 3)]),
        ("abc", ["a", "b", "c", "d"], None, [(0, 1), (1, 2), (2, 3), None]),
        (
            "abc",
            ["a", "b", "c", "d"],
            {"allow_overlap": False},
            [(0, 1), (1, 2), (2, 3), None],
        ),
        (
            "abc",
            ["a", "b", "c", "d"],
            {"allow_overlap": True},
            [(0, 1), (1, 2), (2, 3), None],
        ),
        (
            "abcdef",
            ["ab", "bc", "cd", "de"],
            {"allow_overlap": True},
            [(0, 2), (1, 3), (2, 4), (3, 5)],
        ),
        (
            "abcdef",
            ["ab", "bc", "cd", "de"],
            {"allow_overlap": False},
            [(0, 2), None, (2, 4), None],
        ),
    ],
)
def test_naive_basic(source_text, chunks, options, expected):
    """Test conversion for typical alphabetic strings, including uppercase mix."""
    result = to_offsets(source_text, chunks, options)
    assert result == expected


def test_naive_sequence(
    markdown_source, seq_chunk_1, seq_chunk_2, seq_chunk_3, seq_offsets
):
    """Test conversion for a long text with multiple chunks."""
    result = to_offsets(markdown_source, [seq_chunk_1, seq_chunk_2, seq_chunk_3])
    assert result == seq_offsets


def test_naive_overlap(
    markdown_source,
    overlap_chunk_1,
    overlap_chunk_2,
    overlap_chunk_3,
    overlap_chunk_4,
    overlap_offsets,
):
    """Test conversion for a long text with overlapping chunks."""
    result = to_offsets(
        markdown_source,
        [overlap_chunk_1, overlap_chunk_2, overlap_chunk_3, overlap_chunk_4],
    )
    assert result == overlap_offsets

def test_overlap_size(overlap_size_document, overlap_size_chunks, overlap_size_offsets):
    """Test conversion for a long text with overlapping chunks."""
    result = to_offsets(
        overlap_size_document, overlap_size_chunks, {"overlap_size": 15}
    )
    assert result == overlap_size_offsets

def test_performance(benchmark, markdown_source, overlap_chunks):
    result = benchmark(to_offsets, markdown_source, overlap_chunks)
    assert result is not None
