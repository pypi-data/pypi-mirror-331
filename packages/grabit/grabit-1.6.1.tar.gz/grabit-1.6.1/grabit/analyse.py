from grabit.models import FileSize
from typing import List, Tuple


def group_bytes_by_file_endings(
    files: List[FileSize],
) -> List[Tuple[str, List[int]]]:
    """Groups files by their file path endings and sums the bytes and orders on size,
    also includes the total number of files of that type."""
    bytes_table = {}

    for f in files:
        # Frequently, files can have more than one ending. e.g. `.d.ts` instead of `.ts`
        # the method below makes sure we capture the everything past the first dot.
        path = f.path

        # Ignore the dots that can appear at start of file paths
        if path[0] == "." and "\\" in path or "/" in path:
            path = path[1:]

        file_ending = ".".join(path.split(".")[1:])

        if file_ending == "":
            file_ending = "(No Ending)"

        if file_ending in bytes_table:
            bytes_table[file_ending][0] += f.bytes
            bytes_table[file_ending][1] += 1

        else:
            bytes_table[file_ending] = [f.bytes, 1]

    # Order by size
    bytes_list = list(bytes_table.items())
    bytes_list.sort(key=lambda x: x[1])

    return bytes_list
