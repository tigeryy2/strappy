# strappy

Bootstrapped setup tool. Handles install of developer toolchains and standard applications.
Developed for macOS on my Apple Silicon Macbook Air... not tested on other environments.

## Bootstrap

Run this command in your Zsh terminal, to download and run the bootstrap.sh script.

```bash
mkdir -p /tmp/strappy && curl -fsSL -o /tmp/strappy/bootstrap.sh https://raw.githubusercontent.com/tigeryy2/strappy/main/install/bootstrap.sh && chmod +x /tmp/strappy/bootstrap.sh && /tmp/strappy/bootstrap.sh
```

Alternatively, clone this repository, update any configuration files (see `/config` directory), and run:

```bash
./install/bootstrap.sh
```

Once the bootstrap script has completed, you should have the following installed:

1. Homebrew
2. Git
3. Python3
4. Pipenv
5. Oh-My-Zsh
6. Strappy repository cloned to `~/dev/strappy` with pipenv environment created

Next, run if you are happy with the default set of packages, run the following command to install them:

```bash
python ~/dev/strappy/bootstrap.py
```

## Configuration

Configuration files are located in the `/config` directory. For packages installed via homebrew for which the install
process is straightforward, simply add the package name to the relevant section of `brew_packages.toml`. Be sure to
place "cask" packages under the `[packages][cask]` section.

For example, to install `wget`, add `wget` to the list under `[packages][brew]`.

For packages that require additional configuration, such as `nvm` plugins, create a new class that inherits from
`Package` or `BrewPackage` and implement the `install` method.

## Manual Installation

A `setup.py` has been provided to allow the package to be installed via pip.

1. Clone the project using git
2. Create the pipenv environment
3. Run `pipenv install -e .`
    1. This installs the project in editable mode
