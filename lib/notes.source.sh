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
    if [ ! -d "$notes_dir" ]; then
        log INFO "Capsule without Notes section"
        return
    fi

    log INFO "Generating Notes index for $notes_dir"

cat <<NOTES > "$notes_dir/index.gmi.tmp"
# Notes on $DOMAIN

## $SUBTITLE

NOTES

    while read -r gmi_file; do
        # Extract first heading as post title.
        local title=$($SED -n '/^# / { s/# //; p; q; }' \
            "$notes_dir/$gmi_file" | tr '"' "'")
        echo "=> ./$gmi_file $title" >> "$notes_dir/index.gmi.tmp"
    done < <(notes::_get_notes)

cat <<NOTES >> "$notes_dir/index.gmi.tmp"

That were all notes. Hope they were useful!

=> ../ Go back to main site
NOTES

    mv "$notes_dir/index.gmi.tmp" "$notes_dir/index.gmi"
}
