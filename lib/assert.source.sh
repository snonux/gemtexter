# Unit test for whether 2 given strings equal.
assert::equals () {
    local -r result="$1"; shift
    local -r expected="$1"; shift
    local -r callee=${FUNCNAME[1]}

    if [[ "$result" != "$expected" ]]; then
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

# Unit test for whether a given string is not empty.
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

# Unit test for whether a given string contains a substring
assert::contains () {
    local -r content="$1"; shift
    local -r substring="$1"; shift
    local -r callee=${FUNCNAME[1]}

    if ! $GREP -q -F "$substring" <<< "$content"; then
        log ERROR "In $callee expected '$content' to contain substring '$substring'"
        exit 2
    fi

    log VERBOSE "Substring check in $callee as expected, contains '$substring'"
}

# Unit test for whether a given string matches a regex.
assert::matches () {
    local -r name="$1"; shift
    local -r content="$1"; shift
    local -r regex="$1"; shift
    local -r callee=${FUNCNAME[1]}

    if ! $GREP -q -E "$regex" <<< "$content"; then
        log ERROR "In $callee expected '$name' to match '$regex'"
        exit 2
    fi

    log VERBOSE "Matching in $callee as expected"
}

# Checks if all the Bash scripts here are good.
assert::shellcheck () {
    set -e
    shellcheck \
        --norc \
        --external-sources \
        --check-sourced \
        --exclude=SC2155,SC2010,SC2154,SC1090,SC2012,SC2016 \
        ./"$0"
    set +e
}
