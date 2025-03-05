import os
import platform
import argparse
import subprocess
from pathlib import Path
import re
from typing import List, Set, Tuple, Dict, Any
from grabit.models import File, FileSize
from datetime import datetime
from grabit.present import generate_file_table, generate_file_bytes_table


def copy_to_clipboard(text: str):
    """Copies text to clipboard based on OS."""
    system = platform.system()
    if system == "Windows":
        process = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
        process.communicate(input=text.encode("utf-8"))
    elif system == "Darwin":  # macOS
        process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        process.communicate(input=text.encode("utf-8"))


def read_dot_grabit(directory: str) -> Tuple[Set[str], str, Dict[str, Any]]:
    """
    Reads a .grabit file (if present) and returns:
    - A set of patterns as re.compile objects to ignore
    - A custom message to prepend to the context (if specified)
    - A list of the options included in the .grabit file
    """
    dot_grabit_path = Path(directory) / ".grabit"
    ignore_patterns = set()
    custom_message = (
        "Below is a list of related files, their contents and git history.\n\n"
    )

    # Options
    options = {"git_file_logs": True, "git_all_logs": False}

    if dot_grabit_path.exists():
        print("--- Found .grabit ---")
        current_section = None
        message_lines = []

        with open(dot_grabit_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("## "):
                    current_section = line[3:].lower()
                    continue

                if not line or line.startswith(
                    "//"
                ):  # Skip comments and empty lines
                    continue

                # Gathering include exclude
                if current_section == "exclude":
                    ignore_patterns.add(re.compile(line))
                elif current_section == "message":
                    message_lines.append(line)

                # Gathering the options
                elif current_section == "git file logs":
                    if "true" in line:
                        options["git_file_logs"] = True
                    elif "false" in line:
                        options["git_file_logs"] = False

                elif current_section == "git all logs":
                    if "true" in line:
                        options["git_all_logs"] = True
                    elif "false" in line:
                        options["git_all_logs"] = False

        if message_lines:
            custom_message = "\n".join(message_lines) + "\n\n"

    print("--- ignore patterns ---")
    print(ignore_patterns)
    return ignore_patterns, custom_message, options


def get_all_git_data(path: str) -> str | None:
    """Get all the git logs for the path you've chosen to scan"""
    git_log_cmd = [
        "git",
        "-C",  # Change directory to path before running
        path,
        "log",
        "--pretty=format:%h | %an | %ad | %s",  # Gets the author name, and author date
        "--date=short",
        "--reverse",
    ]

    try:
        result = subprocess.run(
            git_log_cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        history = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running git log: {e}")
        return None

    return history


def get_git_data(file_path: str) -> Tuple[str, datetime, str] | None:
    """
    Gets the git history of the provided file path, and extracts associated data.
    """
    git_log_cmd = [
        "git",
        "log",
        "--follow",
        "--pretty=format:%h | %an | %ad | %s",  # Gets the author name, and author date
        "--date=short",
        file_path,
    ]

    try:
        result = subprocess.run(
            git_log_cmd, capture_output=True, text=True, check=True
        )
        history = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running git log: {e}")
        return None

    if history == "":
        return None

    # If history is not None, get the data
    last_modified_string = history.split("\n")[0].split("|")[2].strip()
    last_modified = datetime.strptime(last_modified_string, "%Y-%m-%d")

    last_author = history.split("\n")[0].split("|")[1].strip()

    return (history, last_modified, last_author)


def is_ignored(
    file_path: str, ignore_patterns: Set[str], base_path: str
) -> bool:
    """Checks if a file matches a regex pattern from the .grabit config."""
    for pattern in ignore_patterns:
        found = pattern.match(file_path)
        if found is not None:
            return True

    return False


def prepare_scan(
    path: str,
    output: str = None,
    to_clipboard: bool = False,
    order: str = None,
    git: bool = True,
):
    """Prepares a context string for AI to read, optionally saves or copies it."""
    ignore_patterns, custom_message, options = read_dot_grabit(path)

    # Apply the options
    if options["git_file_logs"] is False:
        git = False

    files = scan_files(path, ignore_patterns, git=git)

    # The context string builds the message for the LLM
    # It starts with a default message.
    context = (
        "Below is a list of related files, their contents and git history.\n\n"
    )

    if custom_message is not None:
        context = custom_message

    # Add the full git history if asked for
    if options["git_all_logs"]:
        git_history = get_all_git_data(path)

        # Only add if it is a repo
        if git_history is not None:
            context += f"## All the git history for the scanned repo is below:\n{git_history}\n\n"

    # Add all the files
    for file in files:
        print(file.path)
        unix_style_path = file.path.replace("\\", "/")
        context += f"## `{unix_style_path}`:\n### Git History:\n{file.git_history}\n### Contents:\n```\n{file.contents}\n```\n\n"

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(context)
        print(f"Context saved to {output}")

    if to_clipboard:
        print("Context copied to clipboard.")
        copy_to_clipboard(context)

    if not output and not to_clipboard:
        print(context)
        print("\nUse the `-c` flag to copy this context to clipboard.")
        print("Use the `-o <your-file-name>` flag to save it to a file.")

    # Show information to the user for them
    print("--- File Table ---")

    # Order the files
    if order is not None:
        # Get sorting details
        if ":" in order:
            column, direction = order.split(":")
        else:
            column, direction = order, None

        reverse = direction == "desc"

        if column == "path":
            files.sort(key=lambda x: x.path, reverse=reverse)
        elif column == "tokens":
            files.sort(key=lambda x: x.tokens, reverse=reverse)
        elif column == "author":
            files.sort(
                key=lambda x: (x.last_author is None, x.last_author),
                reverse=reverse,
            )
        elif column == "modified":
            files.sort(
                key=lambda x: (x.last_modified is None, x.last_modified),
                reverse=reverse,
            )

    print(generate_file_table(files, colour=True))

    print(f"\nPrompt Size: {len(context)} Chars")
    print(f"Prompt Size: {round(len(context)/4)} Tokens (Rough estimate).")
    print(f"Total files: {len(files)}")

    return context


def scan_files(
    path: str,
    ignore_patterns: Set[str],
    data: List[File] = [],
    git: bool = True,
) -> List[File]:
    """Recursively gets all file paths and contents in a directory, respecting .gitignore."""
    directories = [
        d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))
    ]
    files = [
        f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
    ]

    for file in files:
        file_path = os.path.join(path, file)

        if is_ignored(file_path, ignore_patterns, path):
            print(f"Skipping ignored file: {file_path}")
            continue

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                contents = f.read()

            # Adds git history for extra file context for the LLM
            if git:
                git_data = get_git_data(file_path)
            else:
                git_data = None

            if git_data is None:
                git_history = None
                last_author = None
                last_modified = None
            else:
                git_history, last_modified, last_author = git_data

            data.append(
                File(
                    path=file_path,
                    contents=contents,
                    chars=len(contents),
                    tokens=len(contents) // 4,
                    git_history=git_history,
                    last_author=last_author,
                    last_modified=last_modified,
                )
            )

            print(f"Found: {file_path}")
        except Exception as e:
            print(f"Skipping {file_path}: {e}")

    for directory in directories:
        scan_files(
            os.path.join(path, directory),
            ignore_patterns,
            data,
            git=git,
        )

    return data


def prepare_byte_scan(
    path: str,
    output: str = None,
    to_clipboard: bool = False,
    order: str = None,
):
    """Prepares a context string for AI to read, and outputs a table of file sizes."""
    ignore_patterns, _, _ = read_dot_grabit(path)

    file_bytes = byte_scan(path, ignore_patterns)

    # Starting the context
    context = "Below is a list of files and their sizes.\n\n"

    # Order the files
    if order is not None:
        # Get sorting details
        if ":" in order:
            column, direction = order.split(":")
        else:
            column, direction = order, None

        reverse = direction == "desc"

        if column == "path":
            file_bytes.sort(key=lambda x: x.path, reverse=reverse)
        elif column == "bytes":
            file_bytes.sort(key=lambda x: x.bytes, reverse=reverse)
        elif column == "modified":
            file_bytes.sort(
                key=lambda x: (x.last_modified is None, x.last_modified),
                reverse=reverse,
            )

    # Generate the table using the ordered data
    file_sizes_table_coloured = generate_file_bytes_table(
        file_bytes, colour=True
    )
    file_sizes_table = generate_file_bytes_table(file_bytes, colour=True)

    # Print the table for the user
    print(file_sizes_table_coloured)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(file_sizes_table)
        print(f"File sizes saved to {output}")

    if to_clipboard:
        print("File sizes copied to clipboard.")
        copy_to_clipboard(file_sizes_table)

    return file_sizes_table


def byte_scan(
    path: str,
    ignore_patterns: Set[str],
    data: List[FileSize] = [],
) -> List[FileSize]:
    """Returns a list of FileSize objects."""
    directories = [
        d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))
    ]
    files = [
        f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
    ]

    for file in files:
        file_path = os.path.join(path, file)

        if is_ignored(file_path, ignore_patterns, path):
            print(f"Skipping ignored file: {file_path}")
            continue

        try:
            size_bytes = os.path.getsize(file_path)  # Keep it in bytes
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))

            data.append(
                FileSize(
                    path=file_path,
                    bytes=size_bytes,
                    last_modified=last_modified,
                )
            )

            print(f"Found: {file_path}")
        except Exception as e:
            print(f"Skipping {file_path}: {e}")

    for directory in directories:
        byte_scan(os.path.join(path, directory), ignore_patterns, data)

    return data


from grabit.initialisation import init_command


def main():
    """Command-line interface for the script."""
    parser = argparse.ArgumentParser(
        description="Recursively scan a directory, extract file contents, and save/copy them, respecting .gitignore."
    )

    subparser = parser.add_subparsers(dest="command", help="Available commands")

    # Parser for initialising a .grabit file
    init_parser = subparser.add_parser(
        "init", help="Initialize a standard .grabit file in current directory"
    )

    # Parser for scanning files
    scan_parser = subparser.add_parser(
        "scan", help="Scan a directory and save/copy the context"
    )
    scan_parser.add_argument(
        "directory", type=str, help="The directory to scan"
    )
    scan_parser.add_argument(
        "-o", "--output", type=str, help="File to save extracted content"
    )
    scan_parser.add_argument(
        "-c",
        "--clipboard",
        action="store_true",
        help="Copy output to clipboard",
    )
    scan_parser.add_argument(
        "--order",
        type=str,
        help="The ordering to give the results, you can order in desc or asc. The default is the order of the files as they're found. You can order by 'path', 'bytes', 'modified', the default is ascending. If you want descending write the column name, separated by a colon and then the ordering: 'path:desc'",
    )
    scan_parser.add_argument(
        "-ng",
        "--no-git",
        action="store_false",
        help="Sets flag to *NOT* include the git log history of the searched files. This reduces token count and can speed up the scan process. Git history is collected by default.",
    )

    # Parser for getting file bytes
    byte_parser = subparser.add_parser(
        "bytes",
        help="Get all the sizes of files in a directory, faster to quickly figure out exclude and include. Can be used to generate a table that is sent to AI.",
    )
    byte_parser.add_argument(
        "directory", type=str, help="The directory to scan for file sizes."
    )
    byte_parser.add_argument(
        "-o", "--output", type=str, help="File to save extracted content"
    )
    byte_parser.add_argument(
        "-c",
        "--clipboard",
        action="store_true",
        help="Copy output to clipboard",
    )
    byte_parser.add_argument(
        "--order",
        type=str,
        help="The ordering to give the results, you can order in desc or asc. The default is the order of the files as they're found. You can order by 'path', 'tokens', 'author', 'modified', the default is ascending. If you want descending write the column name, separated by a colon and then the ordering: 'path:desc'",
    )

    args = parser.parse_args()

    if args.command == "init":
        init_command()
    elif args.command == "scan":
        prepare_scan(
            args.directory,
            output=args.output,
            to_clipboard=args.clipboard,
            order=args.order,
            git=args.no_git,
        )
    elif args.command == "bytes":
        prepare_byte_scan(
            args.directory,
            output=args.output,
            to_clipboard=args.clipboard,
            order=args.order,
        )


if __name__ == "__main__":
    main()
