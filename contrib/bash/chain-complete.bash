_chain_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _CHAIN_COMPLETE=complete $1 ) )
    return 0
}

complete -F _chain_completion -o default chain;
