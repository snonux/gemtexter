# Filter out blog posts from other files in the gemfeed dir.
gemfeed::get_posts () {
    local -r gemfeed_dir="$CONTENT_BASE_DIR/gemtext/gemfeed"
    local -r gmi_pattern='^[0-9]{4}-[0-9]{2}-[0-9]{2}-.*\.gmi$'

    ls "$gemfeed_dir" | $GREP -F -v DRAFT- | $GREP -E "$gmi_pattern" | sort -r
}

# Add the links from gemfeed/index.gmi to the main index site.
gemfeed::updatemainindex () {
    local -r index_gmi="$CONTENT_BASE_DIR/gemtext/index.gmi"
    local -r gemfeed_dir="$CONTENT_BASE_DIR/gemtext/gemfeed"

    log VERBOSE "Updating $index_gmi with posts from $gemfeed_dir"

    # Remove old gemfeeds from main index
    $SED '/^=> .\/gemfeed\/[0-9].* - .*/d;' "$index_gmi" > "$index_gmi.tmp"
    # Add current gemfeeds to main index
    $SED -E -n '/^=> / { s| ./| ./gemfeed/|; p; }' \
        "$gemfeed_dir/index.gmi" >> "$index_gmi.tmp"

    mv "$index_gmi.tmp" "$index_gmi"
}

gemfeed::_get_word_count () {
    local -r gmi_file="$1"; shift
    $SED '/^```/,/^```/d' "$gmi_file" | wc -w | cut -d' ' -f1
}

# Generate a index.gmi in the ./gemfeed subdir.
gemfeed::generate () {
    local -r gemfeed_dir="$CONTENT_BASE_DIR/gemtext/gemfeed"
    if [ ! -d "$gemfeed_dir" ]; then
        log INFO "Capsule without Gemfeed"
        return
    fi

    log INFO "Generating Gemfeed index for $gemfeed_dir"

cat <<GEMFEED > "$gemfeed_dir/index.gmi.tmp"
# Gemfeed of $DOMAIN

## $SUBTITLE

GEMFEED

    while read -r gmi_file; do
        # Extract first heading as post title.
        local title=$($SED -n '/^# / { s/# //; p; q; }' \
            "$gemfeed_dir/$gmi_file" | tr '"' "'")

        # Extract the date from the file name, and also get the word count.
        local filename_date=$(basename "$gemfeed_dir/$gmi_file" | cut -d- -f1,2,3)

        local words=$(printf %04d "$(gemfeed::_get_word_count "$gemfeed_dir/$gmi_file")")
        echo "$words words long: $title"

        echo "=> ./$gmi_file $filename_date - $title" >> \
            "$gemfeed_dir/index.gmi.tmp"
    done < <(gemfeed::get_posts)

    mv "$gemfeed_dir/index.gmi.tmp" "$gemfeed_dir/index.gmi"


    gemfeed::updatemainindex
}
