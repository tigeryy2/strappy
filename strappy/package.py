"""
Provides base class for package installation configs
"""
import os
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Optional

from pydantic.dataclasses import dataclass

from config.brew_packages import BREW_PACKAGES_TOML_PATH, BREW_PACKAGES_PATH
from strappy import HOME
from strappy.util.loggable import Loggable


@dataclass(kw_only=True)
class Package(Loggable):
    """
    Base class for package installation configs
    """

    name: str = ""
    check_if_installed: bool = (
        True  # check if the package is installed before installing it
    )

    @property
    def dry_run(self) -> bool:
        """
        Check if we are running in dry run mode
        When true, don't actually run any commands

        If `DRY_RUN` exists and is not "false", then default dry_run to True
        This prevents accidental package installations if the user misspells the value


        :return:
        """
        return (
            True
            if (val := os.environ.get("DRY_RUN")) is not None and val.lower() != "false"
            else False
        )

    @property
    def is_installed(self) -> bool:
        """
        Check if the package is installed
        """
        raise NotImplementedError()

    def install(self):
        """
        Install the package
        """
        raise NotImplementedError()

    def post_install_hook(self):
        """
        Hook to run after package installation
        If package installation is skipped, this hook will also be skipped
        """
        pass

    def run_cmd(
        self, cmd: list[str] | str, capture_output: bool = False, shell: bool = False
    ):
        """
        Run a shell command using subprocess.run
        """
        if shell and isinstance(cmd, list):
            cmd = " ".join(cmd)

        self.logger.debug(f"Running '{' '.join(cmd)}'")

        # shell should be false as we are passing a list of args
        # capture output is generally false to allow the user to interact with the installation process if needed
        result = subprocess.run(
            cmd, check=True, shell=shell, capture_output=capture_output, text=True
        )

        # if we captured the output, log it
        if capture_output:
            self.logger.debug(
                f"\nstdout:\n{result.stdout}"
                f"\nstderr:\n{result.stderr}"
                f"\nreturncode: {result.returncode}"
                f"\n"
            )
        return result


@dataclass(kw_only=True)
class BrewPackage(Package):
    """
    Brew package installation config
    """

    name: str = ""  # homebrew name of the package
    use_cask: bool = False  # true for gui apps

    @property
    def dry_run(self) -> bool:
        """
        Check if we are running in dry run mode
        When true, don't actually run any commands

        If `DRY_RUN` exists and is not "false", then default dry_run to True
        This prevents accidental package installations if the user misspells the value


        :return:
        """
        return (
            True
            if (val := os.environ.get("DRY_RUN")) is not None and val.lower() != "false"
            else False
        )

    @property
    def is_installed(self) -> bool:
        """
        Check if the package is installed
        """
        # cask apps (e.g. gui apps) are a little more complex to check if installed
        if self.use_cask and self.check_cask_app_is_installed():
            self.logger.info(f"{self.name} is already installed")
            return True

        # run with `capture_output=True` to suppress output and avoid printing extra stuff to the console
        try:
            # if brew is able to list the package files, then it is installed
            # probably this could be a little faster if we instead list all brew installed apps and check if the
            # package is in that list? but this is fine for now
            return (
                self.run_cmd(
                    ["brew", "list", self.name], capture_output=True
                ).returncode
                == 0
            )
        except subprocess.CalledProcessError as err:
            self.logger.debug(
                f"Failed to run 'brew list {self.name}' with exception: {err}\n"
                f"This likely means that the package is not installed yet"
            )
            return False

    def get_cask_bundle_name(self) -> Optional[str]:
        """
        Get the bundle name for a cask app, if possible

        This works well for any brew cask that installs an app in `Applications` directly. However, some casks may
        be problematic. For example, 'logi-options-plus' is installed in `Applications` but this is done with an
        installer... we can't just parse the final bundle name from the `brew info` output.

        :return:
        """
        try:
            info_output = self.run_cmd(
                ["brew", "info", "--cask", self.name], capture_output=True
            ).stdout
        except subprocess.CalledProcessError as err:
            self.logger.debug(
                f"Failed to run 'brew info --cask {self.name}', does the cask exist?: {err}"
            )
            return None

        # parse the info output using regex. This pattern will work well for any cask that directly copies {name}.app to
        # `Applications`. However, some casks may be problematic.
        if not (
            (match := re.search(r"==> Artifacts\n(.*) \(App\)\n", info_output))
            and (bundle_name := match.group(1))
        ):
            self.logger.debug(
                f"\n{f' Could not find bundle name for {self.name} ':=^80}"
                f"\n'brew info --cask {self.name}' output:"
                f"\n{info_output}"
                f"\n{'=' * 80}\n"
            )
            return None
        self.logger.debug(f"Found bundle name: '{bundle_name}'")
        return bundle_name

    def check_cask_app_is_installed(self) -> bool:
        """
        Check if an GUI app (e.g. lives in `Applications`) is installed

        This is a little complex because an app may be installed outside of homebrew, in which case, `brew list` will
        not show the app. We need to check if the app exists in `Applications` instead.

        :return:
        """
        try:
            # first check if the app is installed via homebrew
            self.logger.debug(f"Checking if {self.name} is installed via homebrew")
            if (
                self.run_cmd(
                    ["brew", "list", "--cask", self.name], capture_output=True
                ).returncode
                == 0
            ):
                return True
        except subprocess.CalledProcessError as err:
            # if the package is not installed, `brew list` will return a non-zero exit code
            self.logger.info(f"{self.name} is not installed via homebrew")
            self.logger.debug(
                f"Failed to run 'brew list --cask {self.name}' with exception: {err}"
            )

        # if the app is not installed via homebrew, check if it exists in `Applications`
        # first we need to parse the `brew info --cask <app>` output to get the bundle name
        bundle_name: Optional[str] = self.get_cask_bundle_name()
        if bundle_name is None:
            # if we couldn't find the bundle name, let's assume not installed
            self.logger.debug(
                f"Could not find bundle name for {self.name} from brew info, assuming not installed"
            )
            return False

        root_applications: Path = Path("/Applications")
        home_applications: Path = HOME / "Applications"
        self.logger.debug(
            f"Checking if {bundle_name} exists in '{root_applications}' and '{home_applications}"
        )
        app_exists: bool = (root_applications / bundle_name).exists() or (
            home_applications / bundle_name
        ).exists()

        return app_exists

    def install(self) -> bool:
        """
        Install the package

        Returns True if the package was installed, False if it was skipped
        """
        if self.check_if_installed and self.is_installed:
            self.logger.info(
                f"{self.name} is already installed, skipping. To force install, set `check_if_installed=False`"
            )
            return False

        # form the install command
        install_cmd: [str] = ["brew", "install"]
        if self.use_cask:
            install_cmd.append("--cask")
        install_cmd.append(self.name)

        if self.dry_run:
            self.logger.info("Dry run, skipping installation")
            return False

        self.logger.info(f"Installing {self.name} with '{' '.join(install_cmd)}'")
        self.run_cmd(install_cmd)

        # run the post install hook
        self.post_install_hook()

        return True


def from_brew_packages_toml(toml: dict) -> [BrewPackage]:
    """
    Parse a list of brew packages from a toml file
    """
    # where toml is a dict of the toml file
    # such as "{'packages': {'brew': ['nvm', 'python'], 'cask': ['google-chrome']}}"
    packages: [BrewPackage] = []

    brew_packages = toml["packages"]["brew"]
    cask_packages = toml["packages"]["cask"]

    for name in brew_packages:
        packages.append(BrewPackage(name=name))

    for name in cask_packages:
        packages.append(BrewPackage(name=name, use_cask=True))

    # the implicit assumption here is that all apps listed here should follow the defaults (e.g. check if installed)
    return packages


def is_instance_or_subclass_of_package(cls: type) -> bool:
    """
    Check if a class is an instance or subclass of `Package`
    """
    # pycharm code inspection doesn't seem to handle pydandic dataclasses well
    # might see a warning about `runtime_checkable`, but I think this is OK
    return isinstance(cls, type) and issubclass(cls, Package)


def load_packages() -> [BrewPackage]:
    """
    Load list of brew packages from the config toml file
    """
    # load the file and decode it as toml
    with open(BREW_PACKAGES_TOML_PATH, "rb") as toml_file:
        toml = tomllib.load(toml_file)

    packages: [BrewPackage] = from_brew_packages_toml(toml)

    # detect all classes that inherit from `Package` in the `config.brew_packages` module
    # iterate over files in directory
    for file in BREW_PACKAGES_PATH.iterdir():
        Loggable.log().debug(f"Checking file '{file.name}'")

        # ignore directories
        if file.is_dir():
            Package.log().warning(f"'{file.name}' is a directory, skipping it")
            continue

        # ignore `.toml` files, we already loaded them via toml
        if file.suffix == ".toml":
            Package.log().warning(f"'{file.name}' is a toml file, skipping it")
            continue

        # ignore `__init__.py` file
        if file.name == "__init__.py":
            Package.log().warning(f"'{file.name}' is an init file, skipping it")
            continue

        # ignore non-python files
        if file.suffix != ".py":
            Package.log().warning(f"'{file.name}' is not a python file, skipping it")
            continue

        # import the module
        module = __import__(f"config.brew_packages.{file.stem}", fromlist=["*"])
        # iterate over all attributes in the module, to find classes that inherit from `Package`
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            # check if the attribute is a class that inherits from `Package`
            if is_instance_or_subclass_of_package(attr):
                # if the attribute is a class that inherits from `Package`, add it to the list of packages
                package = attr()
                if package.name == "":
                    Package.log().warning(
                        f"Package '{package}' does not have a name, skipping it"
                    )
                    continue
                packages.append(package)

    return packages


def install_packages():
    """
    Install all packages
    """
    Loggable.log().info(f"\n{' Installing Brew Packages ':=^80}")

    packages: [BrewPackage] = load_packages()

    installed_packages: [BrewPackage] = []
    skipped_packages: [BrewPackage] = []
    failed_packages: [BrewPackage] = []
    for package in packages:
        try:
            installed = package.install()
            if installed:
                installed_packages.append(package)
            else:
                skipped_packages.append(package)
        except Exception as e:
            Package.log().error(f"Failed to install {package.name}: {e}")
            failed_packages.append(package)

    Package.log().info(
        f"\n{' Brew Package Installation Summary ':=^80}\n"
        f"Total packages requested: {len(packages)}\n"
        f"Total packages installed: {len(installed_packages)}\n"
        f"Total packages skipped: {len(skipped_packages)}\n"
        f"Total packages failed: {len(failed_packages)}\n"
        f"{'=' * 80}\n"
        f"WARNING: Some packages may require system restart to complete installation\n"
        f"{'=' * 80}\n"
    )
