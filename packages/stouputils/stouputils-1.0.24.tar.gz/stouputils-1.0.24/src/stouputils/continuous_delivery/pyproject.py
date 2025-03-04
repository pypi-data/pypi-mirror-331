""" This module contains utilities for reading and writing pyproject.toml files.

- read_pyproject: Read the pyproject.toml file.
- write_pyproject: Write to the pyproject.toml file.

.. image:: https://raw.githubusercontent.com/Stoupy51/stouputils/refs/heads/main/assets/continuous_delivery/pyproject_module.gif
  :alt: stouputils pyproject examples
"""

# Imports
from ..io import super_open
from typing import Any
import toml

def read_pyproject(pyproject_path: str) -> dict[str, Any]:
	""" Read the pyproject.toml file.

	Args:
		pyproject_path: Path to the pyproject.toml file.

	Returns:
		dict[str, Any]: The content of the pyproject.toml file.
	"""
	return toml.load(pyproject_path)

def write_pyproject(pyproject_path: str, pyproject_content: dict[str, Any]) -> None:
	""" Write to the pyproject.toml file.

	Args:
		pyproject_path: Path to the pyproject.toml file.
		pyproject_content: The content to write to the pyproject.toml file.
	"""
	with super_open(pyproject_path, "w") as file:
		toml.dump(pyproject_content, file)

def increment_version(version: str) -> str:
	""" Increment the version.

	Args:
		version: The version to increment. (ex: "0.1.0")

	Returns:
		str: The incremented version. (ex: "0.1.1")
	"""
	version_parts: list[str] = version.split(".")
	version_parts[-1] = str(int(version_parts[-1]) + 1)
	return ".".join(version_parts)

def increment_version_from_pyproject(pyproject_path: str) -> None:
	""" Increment the version in the pyproject.toml file.

	Args:
		pyproject_path: Path to the pyproject.toml file.
	"""
	pyproject_content = read_pyproject(pyproject_path)
	pyproject_content["project"]["version"] = increment_version(pyproject_content["project"]["version"])
	write_pyproject(pyproject_path, pyproject_content)

def get_version_from_pyproject(pyproject_path: str) -> str:
	""" Get the version from the pyproject.toml file.

	Args:
		pyproject_path: Path to the pyproject.toml file.

	Returns:
		str: The version. (ex: "0.1.0")
	"""
	return read_pyproject(pyproject_path)["project"]["version"]

