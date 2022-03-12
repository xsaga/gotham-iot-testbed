"""Utils to parse project files."""

import ast
import re

from pathlib import Path

def get_variable_from_file(fname: Path, varname: str):
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


def parse_project_makefile(makefile: Path):
    """Crappy makefile parser.
    Returns a list of dictionaries, each dictionary contains
    targets, prerequisites and recipes

    targets : prerequisites
        recipe
    """
    with open(makefile, "r", encoding="utf-8") as f:
        contents = f.read()

    # join logical lines (backslash escaped lines)
    contents = re.sub(r"\\\n", "", contents)
    contents = iter(contents.split("\n"))

    rules = []
    line = next(contents)
    try:
        while True:
            # match 'targets : prerequisites' line
            match = re.search(r"^([\w\-./ ]+) ?:(.*)", line)
            if match:
                rule = {"targets": match.group(1).split(),
                        "prerequisites": match.group(2).split()}
                recipes = []
                # scan next lines for recipes starting with \t
                line = next(contents)
                while line.startswith("\t"):
                    recipes.append(line[1:])
                    line = next(contents)
                rule["recipes"] = recipes
                rules.append(rule)
            else:
                line = next(contents)
    except StopIteration:
        pass
    return rules
