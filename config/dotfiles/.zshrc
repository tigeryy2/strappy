alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
# the following seems to work better on macOS
eval "$(pyenv init --path)"
