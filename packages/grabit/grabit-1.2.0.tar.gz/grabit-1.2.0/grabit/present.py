from typing import List, Any, Dict, Callable
from grabit.models import File, FileSize


def format_table(
    headers: List[str],
    rows: List[List[str]],
    column_widths: List[int],
    align_right_columns: List[int] = None,
) -> str:
    """Generic table formatter that handles borders, padding and alignment."""
    if not rows:
        return "No data found"

    if align_right_columns is None:
        align_right_columns = []

    # Calculate total width including borders and padding
    total_width = sum(column_widths) + (3 * len(column_widths)) - 1

    # Create border lines
    top_bottom_border = "+" + "-" * (total_width) + "+"
    separator = "|" + "-" * (total_width) + "|"

    # Format header row
    header = "| "
    for i, (header_text, width) in enumerate(zip(headers, column_widths)):
        alignment = ">" if i in align_right_columns else "<"
        header += f"{header_text:{alignment}{width}} | "

    # Format data rows
    formatted_rows = []
    for row in rows:
        formatted_row = "| "
        for i, (cell, width) in enumerate(zip(row, column_widths)):
            alignment = ">" if i in align_right_columns else "<"
            formatted_row += f"{cell:{alignment}{width}} | "
        formatted_rows.append(formatted_row)

    # Combine all parts
    return "\n".join(
        [top_bottom_border, header, separator] + formatted_rows + [top_bottom_border]
    )


def generate_file_table(files: List[File]) -> str:
    """Generates a formatted table showing file info including paths, sizes and git history."""
    if not files:
        return "No files found"

    # Get the last commit info for each file
    rows = []
    for file in files:
        if file.git_history:
            # Git history format is: hash | author | date | message
            last_commit = file.git_history.split("\n")[0].split(" | ")
            author, date = last_commit[1], last_commit[2]
        else:
            author, date = "Unknown", "Unknown"

        rows.append(
            [file.path, str(len(file.contents)), str(file.tokens), author, date]
        )

    # Calculate column widths
    headers = ["File Path", "Size (chars)", "Tokens", "Last Modified By", "Date"]
    widths = [
        max(len(header), max(len(row[i]) for row in rows))
        for i, header in enumerate(headers)
    ]

    return format_table(
        headers=headers,
        rows=rows,
        column_widths=widths,
        align_right_columns=[1, 2],  # Size and tokens columns right-aligned
    )


def generate_file_size_table(files: List[FileSize]) -> str:
    """Generates a formatted table showing file sizes and last modified dates."""
    if not files:
        return "No files found"

    rows = [
        [file.path, f"{file.size:.2f}", file.last_modified.strftime("%Y-%m-%d")]
        for file in files
    ]

    headers = ["File Path", "Size (MB)", "Last Modified"]
    widths = [
        max(len(header), max(len(row[i]) for row in rows))
        for i, header in enumerate(headers)
    ]

    return format_table(
        headers=headers,
        rows=rows,
        column_widths=widths,
        align_right_columns=[1],  # Size column right-aligned
    )
