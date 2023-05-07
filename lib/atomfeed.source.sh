atomfeed::_from_cache () {
    local -r gmi_file_path="$1"; shift
    local -r cache_file_path="$1"; shift

    if [ ! -f "${cache_file_path}.info" ]; then
        # No cache there.
        return 1
    elif ! diff "${cache_file_path}.info" <(ls -l "$gmi_file_path") >/dev/null; then
        # Need to refresh the cache.
        return 1
    fi

    log VERBOSE "Retrieving feed content for $gmi_file_path from $cache_file_path"
    cat "$cache_file_path"
}

atomfeed::_make_cache () {
    local -r gmi_file_path="$1"; shift
    local -r cache_file_path="$1"; shift

    log VERBOSE "Making feed content cache from $gmi_file_path"

    local -r cache_file_dir="$(dirname "$cache_file_path")"
    if [ ! -d "$cache_file_dir" ]; then
        mkdir -p "$cache_file_dir"
    fi

    # sed: Remove all before the first header
    # sed: Make HTML links absolute, Atom relative URLs feature seems a mess
    # across different Atom clients.
    html::fromgmi < <($SED '/Go back to the main site/d' "$gmi_file_path") |
    $SED "s|href=\"\./|href=\"https://$DOMAIN/gemfeed/|g;
          s|src=\"\./|src=\"https://$DOMAIN/gemfeed/|g;" |
    tee "$cache_file_path"

    ls -l "$gmi_file_path" > "${cache_file_path}.info"
}

# Retrieve the core content as XHTML of the blog post.
atomfeed::content () {
    local -r gmi_file_path="$1"; shift
    local -r cache_file_path="${gmi_file_path/gemtext/cache}.atomcache"

    atomfeed::_from_cache "$gmi_file_path" "$cache_file_path" ||
        atomfeed::_make_cache "$gmi_file_path" "$cache_file_path"
}

# Generate an atom.xml feed file.
atomfeed::generate () {
    local -r gemfeed_dir="$CONTENT_BASE_DIR/gemtext/gemfeed"

    if [ ! -d "$gemfeed_dir" ]; then
        return
    elif [ -n "$CONTENT_FILTER" ]; then
        log WARN "Not generating Atom feed in filter mode"
        return
    fi

    local -r atom_file="$gemfeed_dir/atom.xml"

    log INFO "Generating Atom feed to $atom_file"
    log INFO 'This may takes a while with an empty cache....'

    cat <<ATOMHEADER > "$atom_file.tmp"
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <updated>$($DATE $DATE_FORMAT)</updated>
    <title>$DOMAIN feed</title>
    <subtitle>$SUBTITLE</subtitle>
    <link href="gemini://$DOMAIN/gemfeed/atom.xml" rel="self" />
    <link href="gemini://$DOMAIN/" />
    <id>gemini://$DOMAIN/</id>
ATOMHEADER

    while read -r gmi_file; do
        atomfeed::_entry "$gemfeed_dir" "$gmi_file" "$atom_file.tmp"
    done < <(gemfeed::get_posts | head -n "$ATOM_MAX_ENTRIES")

    cat <<ATOMFOOTER >> "$atom_file.tmp"
</feed>
ATOMFOOTER
    atomfeed::xmllint "$atom_file.tmp"

    # Delete the 3rd line of the atom feeds (global feed update timestamp)
    if ! diff -u <($SED 3d "$atom_file") <($SED 3d "$atom_file.tmp"); then
        log INFO 'Feed got something new!'
        mv "$atom_file.tmp" "$atom_file"
    else
        log INFO 'Nothing really new in the feed'
        rm "$atom_file.tmp"
    fi
}

atomfeed::_entry () {
    local -r gemfeed_dir="$1"; shift
    local -r gmi_file="$1"; shift
    local -r tmp_atom_file="$1"; shift

    log INFO "Generating Atom feed entry for $gmi_file"

    # Get HTML content for the feed
    local content="$(atomfeed::content "$gemfeed_dir/$gmi_file")"
    assert::not_empty content "$content"

    # Extract first heading as post title.
    local title=$($SED -n '/^# / { s/# //; p; q; }' "$gemfeed_dir/$gmi_file" | tr '"' "'")
    assert::not_empty title "$title"

    # Extract first paragraph from Gemtext as the summary.
    local summary=$($SED -n '/^[A-Z]/ { p; q; }' "$gemfeed_dir/$gmi_file" | tr '"' "'")
    if [ -z "$summary" ]; then
        # No summary found, maybe there is only a quote...
        summary=$($SED -n '/^>/ { s/> *//; p; q; }' "$gemfeed_dir/$gmi_file" | tr '"' "'")
    fi
    assert::not_empty summary "$summary"

    # Extract the date from the file name.
    local date=$(head "$gemfeed_dir/$gmi_file" | $SED -n '/^> Published at / { s/.*Published at //; s/;.*//; p; }')
    if [ -z "$date" ]; then
        # Extract the date from the file.
        date=$($DATE $DATE_FORMAT --reference "$gemfeed_dir/$gmi_file")
        log WARN "No publishing date specified for $gmi_file, assuming $date"
        atomfeed::_insert_date "$date" "$gemfeed_dir/$gmi_file"

    else
        log INFO "Publishing date is $date"
    fi
    assert::not_empty publishing_date "$date"

    cat <<ATOMENTRY >> "$tmp_atom_file"
    <entry>
        <title>$title</title>
        <link href="gemini://$DOMAIN/gemfeed/$gmi_file" />
        <id>gemini://$DOMAIN/gemfeed/$gmi_file</id>
        <updated>$date</updated>
        <author>
            <name>$AUTHOR</name>
            <email>$EMAIL</email>
        </author>
        <summary>$summary</summary>
        <content type="xhtml">
            <div xmlns="http://www.w3.org/1999/xhtml">
                $content
            </div>
        </content>
    </entry>
ATOMENTRY
}

atomfeed::xmllint () {
    local -r atom_feed="$1"

    if [ -n "$XMLLINT" ]; then
        log INFO 'XMLLinting Atom feed'
        if ! $XMLLINT "$atom_feed" >/dev/null; then
            log PANIC "Atom feed $atom_feed isn't valid XML, please re-try"
            return 2
        fi
        log INFO 'Atom feed is OK'
    else
        log WARN 'Skipping XMLLinting Atom feed as "xmllint" command is no installed!'
    fi
}

atomfeed::_insert_date () {
    local -r date="$1"; shift
    local -r gmi_file_path="$1"; shift

    # Insert below first header
    {
        $SED '/^#/q' "$gmi_file_path"
        echo
        echo "> Published at $date"
        $SED -n '/^#/,$p' "$gmi_file_path" | $SED 1d
    } > "$gmi_file_path.insert.tmp"

    mv "$gmi_file_path.insert.tmp" "$gmi_file_path"

    if [ -f "$gmi_file_path.tpl" ]; then
        atomfeed::_insert_date "$date" "$gmi_file_path.tpl"
    fi
}
