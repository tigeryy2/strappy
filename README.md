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
3. uv (manages Python 3.13)
4. Oh-My-Zsh
5. Strappy repository cloned to `~/Documents/dev/strappy` with uv environment synced

Next, if you are happy with the default set of packages, run:

```bash
cd ~/Documents/dev/strappy
uv sync --locked --group dev
uv run --locked python -m strappy.bootstrap
```

## Configuration

Configuration files are located in the `/config` directory. For packages installed via homebrew for which the install
process is straightforward, simply add the package name to the relevant section of `brew_packages.toml`. Be sure to
place "cask" packages under the `[packages][cask]` section.

For example, to install `wget`, add `wget` to the list under `[packages][brew]`.

For packages that require additional configuration, such as `nvm`, create a new class that inherits from
`Package` or `BrewPackage` and implement the `install` method. Add additional scripting to the `post_install_hook`
for any additional configuration that needs to be done after the package is installed.

## Manual Installation

A `pyproject.toml` has been provided to allow the package to be installed via uv.

1. Clone the project using git
2. Run `uv sync --locked --group dev`
3. For submodules, run `uv pip install -e path-to-submodule`
