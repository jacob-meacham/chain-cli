_chain_completion() {
    local cur
    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    prev=${COMP_WORDS[COMP_CWORD-1]}

    # TODO: This should probably be done in Click, rather than here.
    if [[ $cur == add* || ($prev == add* && $cur != -*) ]]; then
        if [[ -z $cur ]]; then
            # No prefix, so just get all names
            COMPREPLY=( $($1 ls -q) );
        else
            # Prefix, so pass that in for the filter
            COMPREPLY=( $($1 ls -q --prefix $cur) );
        fi
    else
        # Use click's standard completion
        COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                           COMP_CWORD=$COMP_CWORD \
                        _CHAIN_COMPLETE=complete $1 ) );
    fi

    return 0
}

complete -F _chain_completion -o default chain;
