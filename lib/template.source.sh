template::generate () {
    log INFO 'Generating files from templates'
    local -i num_tpl_files=0

    while read -r tpl_path; do
        if test -n "$CONTENT_FILTER" && ! $GREP -q "$CONTENT_FILTER" <<< "$tpl_path"; then
            continue
        fi
        num_tpl_files=$(( num_tpl_files + 1 ))
        template::_generate "$tpl_path" &
    done < <(find "$CONTENT_BASE_DIR/gemtext" -type f -name \*.gmi.tpl)

    wait
    log INFO "Converted $num_tpl_files template files"
}

template::_generate () {
    local -r tpl_path="$1"; shift
    local -r tpl_dir="$(dirname "$tpl_path")"
    local -r tpl="$(basename "$tpl_path")"
    local -r dest="${tpl/.tpl/}"

    cd "$tpl_dir" || log PANIC "Unable to chdir to $tpl_dir"
    log INFO "$tpl_path -> $dest"

    while IFS='' read -r line; do
        case "$line" in
            '<< '*)
                template::_line "$line"
                ;;
            *)
                echo "$line"
                ;;
        esac
    done < "$tpl" > "$dest.tmp"

    mv "$dest.tmp" "$dest"
    cd -
}

template::_line () {
    eval "${1/<< /}"
}

template::test () {
    assert::equals "$(template::_line '<< echo -n foo')" 'foo'
    assert::equals "$(template::_line '<< echo foo')" 'foo'
    assert::equals "$(template::_line '<< $DATE --date @0 +%Y%m%d')" '19700101'
    assert::equals "$(template::_line '<< echo "$AUTHOR"')" "$AUTHOR"
}
