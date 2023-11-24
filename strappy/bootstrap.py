import os
import shutil
from datetime import datetime
from pathlib import Path

from config import DOTFILES_DIR, INSTALL_IGNORE_FILES
from config.dotfiles import DOTFILES_TO_OVERWRITE, DOTFILES_TO_APPEND
from logs import LOG_DIR
from strappy.util.loggable import Loggable

HOME = Path("~").expanduser()


def merge_dotfiles(current: Path, new_file: Path) -> Path:
    """
    Merge two dotfiles together

    To avoid repeating the same lines in the dotfiles, we will only append lines that do not already exist in `current`.

    :param current: User's current dotfile in the `HOME` directory. e.g. '~/.zshrc
    :param new_file: New dotfile that needs to be merged into `current`. e.g. 'config/dotfiles/.zshrc'
    :return: Path to the merged dotfile
    """
    # read all lines in the current dotfile
    current_lines = current.read_text().splitlines()

    lines_appended: [str] = []
    # open the current dotfile in append mode
    with current.open("a") as curr:
        # for each line in the new dotfile
        for line in new_file.read_text().splitlines():
            # if the line already exists in the current dotfile, skip it
            if line in current_lines:
                continue
            # otherwise, append it to the current dotfile
            lines_appended.append(line)
            curr.write(f"\n{line}")

    Loggable.log().info(
        f"Appended {len(lines_appended)} lines to '{current.name}':\n"
        + "\n".join([f"  {line}" for line in lines_appended])
        + "\n"
    )
    return current


def install_dotfiles():
    """Install dotfiles from the dotfiles directory"""
    for file in DOTFILES_DIR.iterdir():
        if not file.is_file():
            # make sure we're skipping all non-files
            Loggable.log().warning(f"'{file.name}' is not a file, skipping it")
            continue

        if file.name in INSTALL_IGNORE_FILES:
            # make sure we're skipping all ignored files
            Loggable.log().warning(
                f"'{file.name}' is in INSTALL_IGNORE_FILES, skipping it"
            )
            continue

        # if file exists at destination, back it up and handle according to the defined rules
        if (destination := (HOME / file.name)).exists():
            Loggable.log().info(f"Backing up '{destination}' to '{file.name}.bak'")
            if (backup := HOME / f"{file.name}.bak").exists():
                # if the backup already exists, copy a backup to the logs directory with timestamp, then delete it
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                shutil.copy2(backup, LOG_DIR / f"{file.name}_{timestamp}.bak")
                os.remove(backup)

            # make a copy to back up the dotfile
            shutil.copy2((HOME / file.name), backup)

            if (file_name := file.name) in DOTFILES_TO_OVERWRITE:
                # overwrite the file
                Loggable.log().info(f"Overwriting '{file_name}' at '{destination}'")
                # delete the file at the destination
                os.remove(destination)
                destination.symlink_to(file)
            elif file_name in DOTFILES_TO_APPEND:
                # append to the file
                Loggable.log().info(f"Appending to '{file_name}' at '{destination}'")
                merge_dotfiles(destination, file)
        else:
            # file does not exist at HOME, create a symlink
            Loggable.log().info(
                f"Creating symlink for '{file.name}' at '{destination}'"
            )
            (HOME / file.name).symlink_to(file)


def main():
    Loggable.setup(log_path=LOG_DIR / "bootstrap_py.log")
    install_dotfiles()


if __name__ == "__main__":
    main()
