import tomllib

from pydantic.dataclasses import dataclass

from config.brew_packages import BREW_PACKAGES_TOML_PATH
from config.brew_packages.nvm_package import NvmPackage
from strappy.package import (
    Package,
    BrewPackage,
    from_brew_packages_toml,
    is_instance_or_subclass_of_package,
)


def test_package_run_cmd():
    """
    Test `run_cmd` method
    """

    package = Package(name="test_package")
    result = package.run_cmd(["echo", "hello"])
    # assert result.stdout == "hello\n"
    assert package.name == "test_package"

    result = package.run_cmd(["ping", "www.google.com", "-c", "4"])
    assert result.returncode == 0


def test_brew_package_is_installed():
    """
    Test `is_installed` method
    """
    # if python isn't installed... how are you running this test?
    # in more serious terms, assumes that python is installed under homebrew
    package = BrewPackage(name="python")
    assert package.is_installed

    package = BrewPackage(name="does_not_exist")
    assert not package.is_installed


def test_load_brew_packages():
    """
    Test `load_brew_packages` method
    """

    with open(BREW_PACKAGES_TOML_PATH, "rb") as toml_file:
        toml = tomllib.load(toml_file)
        packages = from_brew_packages_toml(toml)

        assert len(packages) > 0

        for package in packages:
            assert isinstance(package, BrewPackage)


def test_dry_run_install():
    """
    Test `install` method with `dry_run=True`
    """
    package = NvmPackage(dry_run=True)
    package.install()


def test_is_instance_or_subclass_of_package():
    """
    Test `is_instance_or_subclass_of_package` method
    """

    @dataclass
    class SomeClass(Package):
        pass

    @dataclass
    class SomeOtherClass(SomeClass):
        pass

    @dataclass
    class SomeOtherClass2:
        pass

    assert is_instance_or_subclass_of_package(SomeOtherClass)
    assert is_instance_or_subclass_of_package(SomeClass)
    assert not is_instance_or_subclass_of_package(SomeOtherClass2)

    assert is_instance_or_subclass_of_package(NvmPackage)
    assert is_instance_or_subclass_of_package(Package)
    assert not is_instance_or_subclass_of_package("not a class")
    assert not is_instance_or_subclass_of_package(1)
    assert not is_instance_or_subclass_of_package(True)


def test_check_cask_app_is_installed():
    """
    Test `check_cask_app_is_installed` method
    """
    package = BrewPackage(name="google-chrome", use_cask=True)
    assert package.is_installed

    package = BrewPackage(name="google-chrome", use_cask=False)
    assert not package.is_installed

    package = BrewPackage(name="does-not-exist", use_cask=True)
    assert not package.is_installed

    package = BrewPackage(name="does-not-exist", use_cask=False)
    assert not package.is_installed
