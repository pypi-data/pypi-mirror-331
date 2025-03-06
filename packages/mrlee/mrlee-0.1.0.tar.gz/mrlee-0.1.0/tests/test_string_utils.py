import pytest
import re
from simplekit.string_utils import group, matchstr, mget

def test_group():
    """Test grouping items by their first element."""
    items = [("a", 1), ("b", 2), ("a", 3), ("c", 4)]
    expected = {"a": [1, 3], "b": [2], "c": [4]}
    assert group(items) == expected

    # Test invalid input
    with pytest.raises(AssertionError):
        group("not a list or tuple")

    with pytest.raises(ValueError):
        group([("a", 1), ("b")])  # Invalid tuple length

def test_matchstr():
    """Test regex matching and group extraction."""
    # Test single group
    assert matchstr("The price is $10.99", r"\$(\d+\.\d+)") == "10.99"

    # Test multiple groups
    assert matchstr("Name: John, Age: 30", r"Name: (\w+), Age: (\d+)") == ("John", "30")

    # Test no match
    assert matchstr("Hello, World!", r"\d+") is None

    # Test full match (no groups)
    assert matchstr("Hello, World!", r"Hello") == "Hello"

def test_mget():
    """Test extracting and removing the first regex match."""
    # Test successful match
    assert mget("hello world", "world") == ("hello ", "world")

    # Test case-insensitive match
    assert mget("Hello World", "hello", flags=re.IGNORECASE) == (" World", "Hello")

    # Test no match
    assert mget("hello world", "notfound") == ("hello world", None)

    # Test partial match
    assert mget("hello world", "o") == ("hell world", "o")
