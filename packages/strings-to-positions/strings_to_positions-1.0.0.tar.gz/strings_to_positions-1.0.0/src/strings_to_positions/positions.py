from typing import List, Union, Optional, Dict, Tuple


class Options:
    def __init__(
        self,
        case_sensitive: bool = True,
        allow_overlap: bool = True,
        overlap_size: Optional[int] = None,
    ):
        self.case_sensitive = case_sensitive
        self.allow_overlap = allow_overlap
        self.overlap_size = overlap_size


def _find_offset_naive(
    source: str, chunk: str, options: Options
) -> Optional[Tuple[int, int]]:
    # Adjust source and chunk based on case sensitivity
    source_cmp = source if options.case_sensitive else source.lower()
    chunk_cmp = chunk if options.case_sensitive else chunk.lower()

    offset = None
    chunk_length = len(chunk)
    idx = source_cmp.find(chunk_cmp)
    offset = (idx, idx + chunk_length)

    return offset if idx != -1 else None


def to_offsets(
    source: str, chunks: List[str], options: Union[Options, dict, None] = None
) -> List[Optional[Tuple[int, int]]]:
    """
    Finds positions of each chunk in the source text.

    Parameters:
      - source: The full text.
      - chunks: A list of substrings to search for in the source.
      - options: A pydantic Options model (or dict) specifying the search parameters.
        - case_sensitive: If True, the search is case-sensitive. Default is True.
        - allow_overlap: If True, allows overlapping matches. Default is True.
        - overlap_size: If specified, the minimum size of overlap to consider. Default is None.

    Returns:
      A list where each element corresponds to a chunk from the input list. Each element is either
      a list of start and end offset (0-indexed) or None if the chunk is not found.
    """
    # Validate or create a default Options instance using pydantic
    if options is None:
        options = Options()  # use default options
    elif isinstance(options, dict):
        try:
            options = Options(**options)
        except ValueError as e:
            raise ValueError(f"Invalid options provided: {e}")

    results: List[Optional[Tuple[int, int]]] = []
    from_index = 0
    for chunk in chunks:
        current_source = source[from_index:]
        inner_offset = _find_offset_naive(current_source, chunk, options)

        # set current_source to the start offset
        if inner_offset is not None:
            start, end = inner_offset
            offset = (start + from_index, end + from_index)
            # if options.allow_overlap is false, set the end to from_index else set the start to from_index
            if not options.allow_overlap:
                from_index = offset[1]
            else:
                # if overlap_size is specified, set the from_index to the start + overlap_size
                if options.overlap_size is not None:
                    from_index = offset[1] - options.overlap_size
                else:
                    from_index = offset[0]
        else:
            # If chunk not found, set to None
            offset = None

        results.append(offset)

    return results


def offset_to_position(
    source: str, offset: Tuple[int, int]
) -> Dict[str, Dict[str, int]]:
    """
    Given a source text and an offset tuple (start, end), return a dict with line (1-indexed),
    column (1-indexed), and the offset for both start and end positions.
    """
    lines = source.splitlines(keepends=True)

    def get_position(offset: int) -> Dict[str, int]:
        current_offset = 0
        for i, line in enumerate(lines, start=1):
            if current_offset + len(line) > offset:
                column = offset - current_offset + 1  # 1-indexed column
                return {"line": i, "column": column, "offset": offset}
            current_offset += len(line)
        # If offset is beyond source length, return the last position.
        return {
            "line": len(lines),
            "column": len(lines[-1]) if lines else 1,
            "offset": offset,
        }

    start_position = get_position(offset[0])
    end_position = get_position(offset[1])

    return {"start": start_position, "end": end_position}
