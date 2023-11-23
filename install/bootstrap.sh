#!/bin/bash

# Function to add a line to a file only if the line doesn't already exist
add_line_to_file_if_not_exist() {
    local line=$1
    local file=$2
    grep -qF -- "$line" "$file" || echo "$line" >> "$file"
}

# Install Homebrew
if ! command -v brew &> /dev/null
then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed."
fi

# Configure Homebrew in Zsh
if [ -n "$ZSH_VERSION" ]; then
    echo "Configuring Homebrew for Zsh..."

    # Detect Homebrew install location and update PATH
    HOMEBREW_PREFIX=$(brew --prefix)
    add_line_to_file_if_not_exist "export PATH=\"$HOMEBREW_PREFIX/bin:$HOMEBREW_PREFIX/sbin:\$PATH\"" ~/.zshrc

    # Source the changes to .zshrc if needed
    source ~/.zshrc
fi

# Install Git and Python3 using Homebrew
echo "Installing Git and Python3..."
brew install git python3

# Add Python3 paths to the system PATH
PYTHON3_PATH=$(python3 -m site --user-base)/bin
add_line_to_file_if_not_exist "export PATH=\"$PYTHON3_PATH:\$PATH\"" ~/.zshrc

# Source the changes to .zshrc
source ~/.zshrc

# Define the target directory for cloning the repository
TARGET_DIR="$HOME/Documents/dev/strappy"

# Create the parent directory if it doesn't exist
if [ ! -d "$(dirname "$TARGET_DIR")" ]; then
    echo "Creating $(dirname "$TARGET_DIR") directory..."
    mkdir -p "$(dirname "$TARGET_DIR")"
fi

# Clone the strappy repository if it doesn't already exist
if [ ! -d "$TARGET_DIR" ]; then
    echo "Cloning the strappy repository..."
    git clone https://github.com/tigeryy2/strappy.git "$TARGET_DIR"
else
    echo "Strappy repository already exists at $TARGET_DIR."
fi


echo "Setup complete."
