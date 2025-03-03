#!/usr/bin/env python3
"""
Utility to trim trailing whitespace from Python files.
Can be run directly or used as a pre-commit hook.
"""

import argparse
import sys
from pathlib import Path


def trim_trailing_whitespace(file_path):
    """
    Remove trailing whitespace from each line in the file.
    Returns True if changes were made, False otherwise.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Strip trailing whitespace from each line
    stripped_lines = [line.rstrip() + "\n" for line in lines]

    # Check if any changes were made
    if stripped_lines == lines:
        return False

    # Write the changes back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(stripped_lines)

    return True


def process_files(files=None, extensions=None, verbose=False):
    """
    Process files to remove trailing whitespace.

    Args:
        files: List of specific files to process
        extensions: List of file extensions to process (if files not specified)
        verbose: Whether to print verbose output
    """
    if files is None:
        if extensions is None:
            extensions = [".py"]

        # Find all files with the specified extensions
        files = []
        for ext in extensions:
            files.extend(Path(".").glob(f"**/*{ext}"))

    modified_count = 0
    for file_path in files:
        if verbose:
            print(f"Processing {file_path}...")

        if trim_trailing_whitespace(file_path):
            modified_count += 1
            if verbose:
                print(f"  Trimmed whitespace in {file_path}")

    if verbose:
        print(f"Modified {modified_count} file(s)")

    return modified_count


def main():
    parser = argparse.ArgumentParser(description="Trim trailing whitespace from files")
    parser.add_argument("files", nargs="*", help="Specific files to process")
    parser.add_argument(
        "--ext",
        "-e",
        action="append",
        default=[".py"],
        help="File extensions to process (default: .py)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")

    args = parser.parse_args()

    if args.files:
        files = [Path(f) for f in args.files]
        extensions = None
    else:
        files = None
        extensions = args.ext

    modified = process_files(files, extensions, args.verbose)

    if args.verbose:
        print(f"Total files modified: {modified}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
