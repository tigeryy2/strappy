from pydantic.dataclasses import dataclass

from strappy.package import BrewPackage


@dataclass(kw_only=True)
class NvmPackage(BrewPackage):
    """
    nvm package installation config

    nvm is a Node Package Manager. It allows you to install and manage multiple versions of node and npm.

    After installing nvm, node, npm, react, and Next.js will be installed.
    """

    name: str = "nvm"
    use_cask: bool = False

    def post_install_hook(self):
        """
        After installing nvm, install node and npm

        :return:
        """
        self.logger.info("Installing node and npm")
        self.run_cmd(["nvm", "install", "node"])
        self.run_cmd(["nvm", "install-latest-npm"])

        self.logger.info("Installing react and Next.js")
        self.run_cmd(
            ["npm", "install", "next@latest", "react@latest", "react-dom@latest"]
        )
