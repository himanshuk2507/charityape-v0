from typing import Any, List


def chunk_list(seq: List[Any] = [], chunk_size: int = 2):
    for index in range(0, len(seq), chunk_size):
        yield seq[index:index + chunk_size]