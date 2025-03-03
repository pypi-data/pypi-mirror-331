"""
This script updates the version in pyproject.toml and VERSION file.
"""

import sys

import toml

if __name__ == "__main__":
    version = sys.argv[1]

    # Update pyproject.toml
    with open("pyproject.toml", "r", encoding="utf-8") as file:
        pyproject_content = toml.load(file)

    pyproject_content["project"]["version"] = version

    with open("pyproject.toml", "w", encoding="utf-8") as file:
        toml.dump(pyproject_content, file)

    # Update VERSION file
    with open("VERSION", "w", encoding="utf-8") as file:
        file.write(version)
