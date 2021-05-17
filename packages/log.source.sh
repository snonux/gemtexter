log () {
    local -r level="$1"; shift

    for message in "$@"; do
        echo "$message"
    done | log::_pipe "$level"
}

log::pipe () {
    log::_pipe "$1"
}

log::_pipe () {
    local -r level="$1"; shift

    if [[ "$level" == VERBOSE && -z "$LOG_VERBOSE" ]]; then
        return
    fi

    local -r callee=${FUNCNAME[2]}
    local -r stamp=$($DATE +%Y%m%d-%H%M%S)

    while read -r line; do
        echo "$level|$stamp|$callee|$line" >&2
    done
}
