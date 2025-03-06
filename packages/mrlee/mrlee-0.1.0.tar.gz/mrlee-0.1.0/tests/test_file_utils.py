import os
import pytest
from simplekit.file_utils import get_extension, writefile, readfile

def test_get_extension():
    """Test extracting file extensions."""
    assert get_extension("example.txt") == "txt"
    assert get_extension("archive.tar.gz") == "gz"
    assert get_extension("no_extension") == ""
    assert get_extension(".hiddenfile") == ""
    # assert get_extension(".hiddenfile") == "hiddenfile"

def test_writefile_and_readfile(tmpdir):
    """Test writing and reading files in various formats."""
    # Test JSON
    json_file = tmpdir.join("data.json")
    writefile(json_file, {"name": "John", "age": 30})
    assert readfile(json_file) == {"name": "John", "age": 30}

    # Test YAML
    yaml_file = tmpdir.join("config.yaml")
    writefile(yaml_file, {"server": {"host": "localhost", "port": 8080}})
    assert readfile(yaml_file) == {"server": {"host": "localhost", "port": 8080}}

    # Test raw text
    txt_file = tmpdir.join("notes.txt")
    writefile(txt_file, "Hello, World!")
    assert readfile(txt_file) == "Hello, World!"

    # Test unsupported format
    with pytest.raises(ValueError):
        writefile(tmpdir.join("unsupported.xyz"), {"key": "value"})

    # Test invalid data type
    with pytest.raises(TypeError):
        writefile(tmpdir.join("invalid.json"), 123)

def test_writefile_directory_creation(tmpdir):
    """Test that directories are created if they don't exist."""
    nested_file = tmpdir.join("nested/folder/data.json")
    writefile(nested_file, {"key": "value"})
    assert os.path.exists(nested_file)
