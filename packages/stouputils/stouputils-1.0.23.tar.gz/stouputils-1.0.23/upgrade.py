
## Python script that modifies the pyproject.toml to go to the next version
# Imports
import stouputils as stp

# Constants
ROOT: str = stp.get_root_path(__file__)
PYPROJECT_PATH = f"{ROOT}/pyproject.toml"
CURRENT_VERSION: str = stp.get_version_from_pyproject(PYPROJECT_PATH)

# Main
if __name__ == "__main__":
	
	# Increment version
	stp.increment_version_from_pyproject(PYPROJECT_PATH)

