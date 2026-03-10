export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
export PATH=~/.npm-global/bin:$PATH
export PATH="$PATH":"$HOME/.pub-cache/bin"

# >>>  >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/anaconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/opt/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/opt/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

export PATH=$PATH:$HOME/.npm-global/bin

. "$HOME/.local/bin/env"

# Added by Windsurf
export PATH="/Users/mahekparvez/.codeium/windsurf/bin:$PATH"

# OpenClaw Completion
source "/Users/mahekparvez/.openclaw/completions/openclaw.zsh"
