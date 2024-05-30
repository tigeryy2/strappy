alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
# the following seems to work better on macOS
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"

# Point pip to configuration file that's loaded last
export PIP_CONFIG_FILE="$HOME/pip.conf"

[ -f /opt/homebrew/etc/profile.d/autojump.sh ] && . /opt/homebrew/etc/profile.d/autojump.sh
eval "$(fzf --zsh)"

# Disable press-and-hold for keys if not already set, helpful for ideaVim
if [[ $(defaults read -g ApplePressAndHoldEnabled) != 0 ]]; then
    defaults write -g ApplePressAndHoldEnabled -bool false
fi