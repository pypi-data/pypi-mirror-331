"""
File-related utilities for reading, writing, and manipulating files.

This module provides functions to handle file operations such as reading and writing
data in various formats (JSON, YAML, TOML, raw text/binary), extracting file extensions,
and ensuring proper directory creation for file paths.

Functions:
    - get_extension: Extracts and formats the file extension from a given path.
    - writefile: Writes data to a file, serializing it based on the file extension.
    - readfile: Reads a file and returns its content, deserializing if applicable.
"""
import os
import json
import yaml
from typing import Any

def get_extension(file_path: str) -> str:
    """Extracts and formats the file extension from a given file path.
       Files like .env and .vimrc will result in no extension.
       The extension is "". This is intended.

    Args:
        file_path: The path to the file (string).

    Returns:
        The file extension in lowercase without the leading dot (string).
        Returns an empty string if no extension is found.
    """
    return os.path.splitext(file_path)[1].lstrip(".").lower()

def writefile(filepath: str, data: Any) -> str:
    """Writes data to a file, serializing it based on the file extension.
    Creates the directory if it doesn't exist.

    Args:
        filepath: The path to the file to write to. The path must have an extension.
        data: The data to write to the file. Supported types include int, float, str,
              bool, dict, and list. Data will be serialized to YAML, TOML, or JSON
              format based on the file extension.

    Returns:
        The absolute path to the file that was written to.

    Raises:
        ValueError: If the file extension is not supported or data is None.
        TypeError: If the data cannot be serialized to the specified format.
        AssertionError: If the data is None or has no value or if the file path
                        does not have an extension.
    """
    assert data, "Data must be existant. Empty strings or None are not allowed."
    assert os.path.splitext(filepath)[1], "Filepath must have an extension."

    def serialize(data: Any) -> str:
        if isinstance(data, (int, bool)):
            raise TypeError("Only strings, arrays, and dictionaries are allowed.")
        if isinstance(data, str):
            return data

        file_extension = get_extension(filepath)

        match file_extension:
            case "yml" | "yaml":
                return yaml.dump(data, indent=2)
            case "toml":
                import toml
                return toml.dumps(data)
            case "json":
                return json.dumps(data, indent=2)
            case _:
                raise ValueError(f"Unsupported file extension: {file_extension}")

    expanded_file_path = os.path.abspath(filepath)

    # Create the directory if it doesn't exist
    dir_path = os.path.dirname(expanded_file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    value = serialize(data)
    with open(expanded_file_path, "w") as file:
        file.write(value)

    return expanded_file_path

def readfile(path: str) -> Any:
    """Reads a file and returns its content.
    Supports JSON, YAML, TOML, and raw text/binary formats.

    Args:
        path: The path to the file.

    Returns:
        The content of the file, deserialized if applicable.
        Returns None if the file does not exist.
    """
    expanded_path = os.path.expanduser(path)

    if not os.path.isfile(expanded_path):
        return None

    extension = get_extension(expanded_path)

    mode = "rb" if extension in ("img", "jpg", "jpeg", "png", "gif", "svg") else "r"
    with open(expanded_path, mode) as f:
        if extension == "json":
            return json.load(f)
        elif extension in ("yaml", "yml"):
            return yaml.safe_load(f)
        elif extension == "toml":
            import toml
            return toml.load(f)
        else:
            return f.read()

print(get_extension('.ab'))
