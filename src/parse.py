"""Parse python source files."""

import ast


def get_variable_from_file(fname: str, varname: str):
    """Parse a python script to get the value of a variable."""
    with open(fname, "r", encoding="utf-8") as f:
        contents = f.read()

    tree = ast.parse(contents)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if (len(node.targets) == 1) and (node.targets[0].id == varname):
                try:
                    return ast.literal_eval(node.value)
                except ValueError:
                    raise ValueError(f"Can't evaluate {varname}.") from None

    raise ValueError(f"Variable {varname} not found.")
