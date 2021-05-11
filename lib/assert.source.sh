assert::equals () {
    local -r result="$1"; shift
    local -r expected="$1"; shift

    if [ "$result" != "$expected" ]; then
        cat <<ERROR
Expected
    '$expected'
But got
    '$result'
ERROR
        exit 2
    fi

    echo "Assert OK: $expected"
}
