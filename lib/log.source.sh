# Log a message.
log () {
    local -r level="$1"; shift
    local message

    for message in "$@"; do
        echo "$message"
    done | log::_pipe "$level" $$
}

# Log a stream through a pipe.
log::pipe () {
    log::_pipe "$1" $$
}

# Internal log implementation.
log::_pipe () {
    local -r level="$1"; shift
    local -r pid="$1"; shift

    if [[ "$level" == VERBOSE && -z "$LOG_VERBOSE" ]]; then
        # Drain stdin instead of returning right away. If we exit without
        # reading, the writer side of the pipe (see log) can get SIGPIPE, and
        # under 'set -e -o pipefail' that aborts the whole run with exit 141.
        cat >/dev/null
        return
    fi

    local -r callee=${FUNCNAME[2]}
    local -r stamp=$($DATE +%Y%m%d-%H%M%S)

    while read -r line; do
        echo "$level|$stamp|$pid|$callee|$line" >&2
    done

    if [ "$level" = PANIC ]; then
        exit 2
    fi
}
