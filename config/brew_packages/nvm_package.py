import os
import subprocess
import tempfile
import textwrap

from pydantic.dataclasses import dataclass

from strappy import HOME
from strappy.package import Package


@dataclass(kw_only=True)
class NvmPackage(Package):
    """
    nvm package installation config

    nvm is a Node Package Manager. It allows you to install and manage multiple versions of node and npm.

    After installing nvm, node, npm, react, and Next.js will be installed.

    Note: since managing nvm via brew is not officially supported, install via the official install script instead.
    """

    name: str = "nvm"

    def is_installed(self) -> bool:
        """
        Check if nvm is installed

        :return: True if nvm is installed, False otherwise
        """
        # consider nvm installed if `.nvm` directory exists at home directory
        return os.path.isdir(HOME / ".nvm")

    def install(self) -> bool:
        """
        Install nvm

        :return: True if nvm was installed successfully, False otherwise
        """
        if self.check_if_installed and self.is_installed:
            self.logger.info(
                f"{self.name} is already installed, skipping. To force install, set `check_if_installed=False`"
            )
            return False

        if self.dry_run:
            self.logger.info("Dry run, skipping nvm installation")
            return True

        self.logger.info("Installing nvm")
        try:
            _ = self.run_cmd(
                "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash",
                shell=True,
                capture_output=False,
            )
        except subprocess.CalledProcessError as err:
            self.logger.error(f"Error installing nvm: {err}")
            return False

        _ = self.post_install_hook()

        return self.is_installed()

    def post_install_hook(self):
        """
        After installing nvm, install node and npm

        :return:
        """
        # Create a temporary shell script file
        with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as temp_script:
            temp_script.write(
                (
                    textwrap.dedent(
                        """/
        #!/bin/zsh

        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # Load nvm

        # Run your subsequent commands
        nvm install node
        nvm install-latest-npm
        npm install next@latest react@latest react-dom@latest

        # Exit with the exit code of the last command
        exit $?
        """
                    ).encode()
                )
            )

        # Make the script executable
        self.run_cmd(["chmod", "+x", temp_script.name])

        # Run the script
        self.logger.info("Installing node, npm, react, and Next.js")
        try:
            _ = self.run_cmd(["zsh", temp_script.name])
        except subprocess.CalledProcessError as err:
            self.logger.error(f"Error installing node, npm, react, and Next.js: {err}")
            os.remove(temp_script.name)
            return False

        os.remove(temp_script.name)
        return True
