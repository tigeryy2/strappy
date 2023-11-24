from pathlib import Path

# Files and Directories
CONFIG_DIR: Path = Path(__file__).parent
DOTFILES_DIR: Path = Path(__file__).parent / "dotfiles"

# special files
INSTALL_IGNORE_FILES: [str] = ["__init__.py"]
