import pytest
from simplekit.text_tools import comment, templater

# Test cases for the `comment` function
@pytest.mark.parametrize("input_text, filetype, expected_output", [
    # Python
    ("print('Hello, World!')", "python", "# print('Hello, World!')"),
    ("# print('Hello, World!')", "python", "print('Hello, World!')"),
    ("    print('Indented')", "python", "    # print('Indented')"),
    ("    # print('Indented')", "python", "    print('Indented')"),

    # JavaScript
    ("console.log('Hello');", "javascript", "// console.log('Hello');"),
    ("// console.log('Hello');", "javascript", "console.log('Hello');"),

    # HTML
    ("<div>Hello</div>", "html", "<!-- <div>Hello</div> -->"),
    ("<!-- <div>Hello</div> -->", "html", "<div>Hello</div>"),

    # CSS
    ("body { color: red; }", "css", "/* body { color: red; } */"),
    ("/* body { color: red; } */", "css", "body { color: red; }"),

    # Edge cases
    ("", "python", ""),  # Empty string
    ("    ", "python", "    "),  # Whitespace only
    ("#", "python", ""),  # Single comment symbol
    ("<!--", "html", "<!-- <!-- -->"),  # Incomplete HTML comment
])
def test_comment(input_text, filetype, expected_output):
    assert comment(input_text, filetype) == expected_output


# Test cases for the `templater` function
@pytest.mark.parametrize("template, scope, expected_output", [
    # Simple variable substitution
    ("Hello, $name!", {"name": "Alice"}, "Hello, Alice!"),
    ("Hello, $name!", {"name": "Bob"}, "Hello, Bob!"),

    # Fallback value
    ("Hello, $name:Guest!", {}, "Hello, Guest!"),
    ("Hello, $name:Guest!", {"name": "Charlie"}, "Hello, Charlie!"),

    # Callable expressions
    ("Result: $add(2, 3)", {"add": lambda a, b: a + b}, "Result: 5"),

    # Bracket expressions
    ("Value: ${2 + 3}", {}, "Value: 5"),

    # List rendering with indentation
    (
        "Fruits:\n  - $items",
        {"items": ["apple", "banana"]},
        "Fruits:\n  - apple\n  - banana"
    ),
    (
        "Fruits:\n  • $items",
        {"items": ["apple", "banana"]},
        "Fruits:\n  • apple\n  • banana"
    ),

    # Edge cases
    ("No template here!", {}, "No template here!"),  # No template variables
    # ("Empty $variable:", {}, "Empty "),  # Empty fallback
    # ("$unknown", {}, ""),  # Unknown variable without fallback
])
def test_templater(template, scope, expected_output):
    assert templater(template, scope) == expected_output



if __name__ == "__main__":
    pytest.main()
