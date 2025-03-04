import inspect
from pathlib import Path
from typing import Optional

import __main__

ROOT_DIR = str(Path(__file__).parents[1])  # pyerrorschema module


def _get_entrypoint() -> Optional[Path]:
    """Get the root directory path of the running program.

    Retrieves the directory containing the main entry point script of the program.
    This is used as a reference point for generating relative file paths in error
    messages.

    Returns:
        Path | None: Directory path of the entry point script, or None if not found
        (e.g., when running from REPL or notebook).
    """
    entrypoint = getattr(__main__, "__file__", None)
    if entrypoint is not None:
        entrypoint = Path(entrypoint).parent
    return entrypoint


def get_caller_location() -> Optional[str]:
    """Get the caller location of the function.

    Walks up the call stack to find the first caller outside of the pyerrorschema
    package. Returns a formatted string containing the file path (relative to program
    entry point), line number, and function name where the error occurred.

    Returns:
        str | None: Formatted location string in the format "file:line:function",
        or None if no suitable caller is found. File paths are made relative to
        the program's entry point directory when possible.

    Example:
        >>> get_caller_location()
        'services/user.py:42:validate_input'
    """
    entrypoint = _get_entrypoint()

    for frame in inspect.stack():
        if frame.filename.startswith(ROOT_DIR):
            continue

        filename = frame.filename
        line = frame.lineno
        function = frame.function
        if entrypoint:
            filename = str(Path(filename).relative_to(entrypoint))

        return f"{filename}:{line}:{function}"

    return None
