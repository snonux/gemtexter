assert::equals () {
    local -r result="$1"; shift
    local -r expected="$1"; shift
    local -r callee=${FUNCNAME[1]}

    if [ "$result" != "$expected" ]; then
        cat <<ERROR | log::pipe ERROR
In $callee expected
    '$expected'
But got
    '$result'
ERROR
        exit 2
    fi

    log VERBOSE "Result in $callee as expected: '$expected'"
}

assert::not_empty () {
    local -r name="$1"; shift
    local -r content="$1"; shift
    local -r callee=${FUNCNAME[1]}

    if [ -z "$content" ]; then
        log ERROR "In $callee expected '$name' not to be empty!"
        exit 2
    fi

    log VERBOSE "Result in $callee as expected not empty"
}
