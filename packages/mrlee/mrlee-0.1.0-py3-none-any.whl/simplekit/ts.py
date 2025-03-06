import tree_sitter
from typing import TypedDict

class TreeData(TypedDict):
    tree: tree_sitter.Tree
    src: str
    language: tree_sitter.Language


def get_tree(text: str, filetype: str) -> TreeData:
    """Parses source code into a tree-sitter tree.

    Args:
        text: The source code to parse as a string.
        filetype: The type of the file, e.g., "python", "javascript", or "typescript".

    Returns:
        A dictionary containing the parsed tree, the source code as a string, and the language object.
        The keys are:
        - "tree": The tree-sitter Tree object representing the parsed code.
        - "src": The source code as a string.
        - "language": The tree-sitter Language object used for parsing.

    Raises:
        ValueError: If the specified filetype is not supported.

    Examples:
        Parsing a simple Python code snippet:
        >>> code = "def foo():\\n    print('hello')\\n"
        >>> tree_data = get_tree(code, "python")
        >>> print(tree_data["tree"].root_node.sexp())
        (module (function_definition name: (identifier) parameters: (parameters) body: (block (expression_statement (call function: (identifier) arguments: (argument_list (string)))))))
    """

    def get_language(filetype: str) -> tree_sitter.Language:
        """Returns the tree-sitter Language object for the given filetype."""
        match filetype:
            case "python":
                import tree_sitter_python
                return tree_sitter.Language(tree_sitter_python.language())
            case "javascript":
                import tree_sitter_javascript
                return tree_sitter.Language(tree_sitter_javascript.language())
            case "typescript":
                import tree_sitter_typescript
                return tree_sitter.Language(tree_sitter_typescript.language())
            case _:
                raise ValueError(f"Unsupported filetype: {filetype}")

    language: tree_sitter.Language = get_language(filetype)
    parser = tree_sitter.Parser()
    parser.language = language

    src_bytes: bytes = bytes(text, "utf8")
    tree: tree_sitter.Tree = parser.parse(src_bytes)

    return {"tree": tree, "src": text, "language": language}









def extract_import_statements_and_group_at_top_of_file(treedata: TreeData) -> str:
    """
    Extracts all import statements from a Python file, removes duplicates,
    groups them at the top of the file, and returns the modified content as a string.

    Args:
        treedata (TreeData): A dictionary containing the parsed tree, source code, and language object.

    Returns:
        str: Modified file content with imports grouped at the top.
    """
    tree = treedata["tree"]
    src = treedata["src"]
    import_statements = []
    non_import_statements = []

    import_node_types = ["import_statement", "from_import_statement"]

    def traverse_tree(node: tree_sitter.Node):
        if node.type in import_node_types:
            import_statements.append(node)
        else:
            non_import_statements.append(node)

    root_node = tree.root_node

    for node in root_node.children:
        if node.type in import_node_types:
            import_statements.append(node)
        else:
            non_import_statements.append(node)

    # Extract text of import statements and remove duplicates
    import_texts = []
    for node in import_statements:
        import_texts.append(src[node.start_byte:node.end_byte])

    unique_import_texts = []
    [unique_import_texts.append(x) for x in import_texts if x not in unique_import_texts]

    # Reconstruct the file content
    new_content = "\n".join(unique_import_texts) + "\n\n"

    non_import_text = ""
    for node in non_import_statements:
        non_import_text += src[node.start_byte:node.end_byte]

    # Remove leading newlines from non-import statements
    non_import_text = non_import_text.lstrip("\n")
    new_content += non_import_text
    return new_content


