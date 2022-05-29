notes::_get_notes () {
    local -r notes_dir="$CONTENT_BASE_DIR/gemtext/notes"
    local -r gmi_pattern='.*\.gmi$'

    ls "$notes_dir" |
        $GREP -E "$gmi_pattern" |
        $GREP -v '^index.gmi$' |
        sort -r
}

# Generate a index.gmi in the ./notes subdir.
notes::generate () {
    local -r notes_dir="$CONTENT_BASE_DIR/gemtext/notes"
    log INFO "Generating Notes index for $notes_dir"

cat <<NOTES > "$notes_dir/index.gmi.tmp"
# Notes on $DOMAIN

## $SUBTITLE

NOTES

    while read -r gmi_file; do
        # Extract first heading as post title.
        local title=$($SED -n '/^# / { s/# //; p; q; }' \
            "$notes_dir/$gmi_file" | tr '"' "'")

        echo "=> ./$gmi_file $title" >> \
            "$notes_dir/index.gmi.tmp"
    done < <(notes::_get_notes)

    mv "$notes_dir/index.gmi.tmp" "$notes_dir/index.gmi"
    git::add gemtext "$notes_dir/index.gmi"
}
