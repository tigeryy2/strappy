alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Point pip to configuration file that's loaded last
export PIP_CONFIG_FILE="$HOME/pip.conf"

[ -f /opt/homebrew/etc/profile.d/autojump.sh ] && . /opt/homebrew/etc/profile.d/autojump.sh
eval "$(fzf --zsh)"

# Disable press-and-hold for keys if not already set, helpful for ideaVim
if [[ $(defaults read -g ApplePressAndHoldEnabled) != 0 ]]; then
    defaults write -g ApplePressAndHoldEnabled -bool false
fi

# setting global env variables
# set vite-devtools 'open-in-editor': https://devtools.vuejs.org/getting-started/open-in-editor
export LAUNCH_EDITOR=webstorm