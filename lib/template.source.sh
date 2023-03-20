template::generate () {
    log INFO 'Generating files from templates'
    local -i num_tpl_files=0

    while read -r tpl_path; do
        if test -n "$CONTENT_FILTER" && ! $GREP -q "$CONTENT_FILTER" <<< "$tpl_path"; then
            continue
        fi
        num_tpl_files=$(( num_tpl_files + 1 ))
        template::_generate_file "$tpl_path"
    done < <(find "$CONTENT_BASE_DIR/gemtext" -type f -name \*.gmi.tpl)

    wait
    log INFO "Converted $num_tpl_files template files"
}

template::_generate_file () {
    local -r tpl_path="$1"; shift
    local -r tpl_dir="$(dirname "$tpl_path")"
    local -r tpl="$(basename "$tpl_path")"
    local -r dest="${tpl/.tpl/}"

    cd "$tpl_dir" || log PANIC "Unable to chdir to $tpl_dir"
    log INFO "$tpl_path -> $dest"

    template::_generate < "$tpl" > "$dest.tmp"
    mv "$dest.tmp" "$dest"
    cd -
}

template::_generate () {
    local is_block=no
    local block=''

    while IFS='' read -r line; do
        if [ "$is_block" = yes ]; then
            if [ "$line" = '>>>' ]; then
                template::_eval "$block"
                is_block=no
                block=''
            else
                block="$block
$line"
            fi
            continue
        fi
        case "$line" in
            '<< '*)
                template::_eval "$line"
                ;;
            '<<<')
                is_block=yes
                ;;
            *)
                echo "$line"
                ;;
        esac
    done
}

template::_eval () {
    eval "${1/<< /}"
}

template::test () {
    assert::equals "$(template::_eval '<< echo -n foo')" 'foo'
    assert::equals "$(template::_eval '<< echo foo')" 'foo'
    assert::equals "$(template::_eval '<< $DATE --date @0 +%Y%m%d')" '19700101'
    assert::equals "$(template::_eval '<< echo "$AUTHOR"')" "$AUTHOR"

    template::_eval '<< foo=bar'
    assert::equals "$(template::_eval '<< echo $foo')" bar

    local -r template1='# Hello Mister
<<<
    echo -n "Epoch 0 starts at: "
    $DATE --date @0 +%Y%m%d
    echo Just so that you know
>>>'
    local -r expect1='# Hello Mister
Epoch 0 starts at: 19700101
Just so that you know'
    assert::equals "$(template::_generate <<< "$template1")" "$expect1"

    local -r template2='<<<
    for i in {1..10}; do
        echo -n $i
    done
>>>'
    assert::equals "$(template::_generate <<< "$template2")" 12345678910

    local -r template3='<<<
    foo=baz
>>>
<<<
    echo $foo
>>>'
    assert::equals "$(template::_generate <<< "$template3")" baz

    local -r template4='<<<
>>>
<<<
>>>
<< :'
    assert::equals "$(template::_generate <<< "$template4")" ''
}
