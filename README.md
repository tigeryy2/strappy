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
