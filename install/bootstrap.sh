#!/bin/zsh

# Function to add a line to a file only if the line doesn't already exist
add_line_to_file_if_not_exist() {
    local line=$1
    local file=$2
    # Check if the line exists in the file
    if ! grep -qF -- "$line" "$file"; then
        # Append the line with a preceding newline, handling the case of no newline at the end of the file
        echo -e "\n$line" >> "$file"
    fi
}

# Variables
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
TEMP_DIR="/tmp/strappy"
LOG_FILE="${TEMP_DIR}/$TIMESTAMP.log"
ZSHRC_BACKUP="$HOME/.zshrc_backup_$TIMESTAMP"
USER_SHELL=$(dscl . -read /Users/$USER UserShell | awk '{print $2}')
# Define the target directory for cloning strappy repository
TARGET_DIR="$HOME/Documents/dev/strappy"
# Define the target log directory in strappy repo
LOG_DIR="$TARGET_DIR/logs"

# Setup Temp dirs and log file
mkdir -p "$TEMP_DIR"
exec > >(tee "$LOG_FILE") 2>&1
echo "Running bootstrap.sh at ${TIMESTAMP}"

# Backup .zshrc file
if [ -f "$HOME/.zshrc" ]; then
    cp "$HOME/.zshrc" "$ZSHRC_BACKUP"
fi

# Install Homebrew
if ! command -v brew &> /dev/null
then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add command to `.zprofile so that homebrew to PATH at terminal startup
    echo 'eval $(/opt/homebrew/bin/brew shellenv)' >> $HOME/.zprofile
    # Add homebrew to path in current terminal
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "Homebrew is already installed."
fi

# Add Homebrew to path as necessary
if [[ "$USER_SHELL" == */zsh ]]; then
    echo "Conditionally adding Homebrew to PATH via ~/.zshrc"

    # Detect Homebrew install location and update PATH
    HOMEBREW_PREFIX=$(brew --prefix)
    add_line_to_file_if_not_exist "export PATH=\"$HOMEBREW_PREFIX/bin:$HOMEBREW_PREFIX/sbin:$HOMEBREW_PREFIX/opt:\$PATH\"" ~/.zshrc

    # Source the changes to .zshrc
    source ~/.zshrc
else
    echo "Warning: Install script untested for non-Zsh shells"
fi

# Install Git using Homebrew
echo "Installing Git..."
brew install git

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    brew install uv
else
    echo "uv is already installed."
fi

# Install Python 3.13 using uv
echo "Installing Python 3.13 via uv..."
uv python install 3.13

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

# Initialize uv environment in the strappy repository
if [ -d "$TARGET_DIR" ]; then
    echo "Syncing uv environment for Strappy..."
    cd "$TARGET_DIR" || exit 1
    uv sync --locked --group dev
fi

# Install Oh My Zsh if not already installed
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo "Installing Oh My Zsh (unattended mode)..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

    # Check if .zshrc.pre-oh-my-zsh exists and append its contents to .zshrc
    if [ -f "$HOME/.zshrc.pre-oh-my-zsh" ]; then
        echo "Adding contents of .zshrc.pre-oh-my-zsh into the end of the new .zshrc"
        echo -e "\n$(cat "$HOME/.zshrc.pre-oh-my-zsh")" >> "$HOME/.zshrc"
    fi
else
    echo "Oh My Zsh is already installed."
fi

echo "Saving logs to ${LOG_DIR}"
# Create the log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Check for duplicate log file in the target directory and rename if necessary
TARGET_LOG_FILE="$LOG_DIR/$(basename "$LOG_FILE")"
if [ -f "$TARGET_LOG_FILE" ]; then
    mv "$TARGET_LOG_FILE" "${TARGET_LOG_FILE}_backup_$(date '+%Y%m%d_%H%M%S')"
fi

# Copy the log file to strappy/logs
mv "$LOG_FILE" "$TARGET_LOG_FILE"
mv "$ZSHRC_BACKUP" "$LOG_DIR"

echo "Setup complete."

# Check if we're not already using Oh My Zsh
if [ -z "$ZSH_VERSION" ] || [ -z "$ZSH" ]; then
    echo "Switching to Zsh..."
    # switch to oh-my-zsh
    exec zsh
else
    echo "Already running Oh My Zsh."
fi
