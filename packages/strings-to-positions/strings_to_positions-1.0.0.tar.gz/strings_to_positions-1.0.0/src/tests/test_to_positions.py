from strings_to_positions import offset_to_position  # import the package to test


def test_offset_to_position(markdown_source, seq_offsets):
    result = offset_to_position(markdown_source, seq_offsets[0])
    assert result == {
        "start": {"line": 1, "column": 1, "offset": 0},
        "end": {"line": 4, "column": 61, "offset": 291},
    }
