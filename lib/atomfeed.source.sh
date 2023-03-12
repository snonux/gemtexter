# Retrieve meta data of a given blog post. Generate new meta info if not yet exists.
atomfeed::meta () {
    local -r gmi_file_path="$1"; shift
    local -r meta_file=$($SED 's|gemtext|meta|; s|.gmi$|.meta|;' <<< "$gmi_file_path")

    log VERBOSE "Generating meta info for post $gmi_file_path"

    local -r meta_dir=$(dirname "$meta_file")
    if [[ ! -d "$meta_dir" ]]; then
        mkdir -p "$meta_dir"
    fi

    if [ ! -f "$meta_file" ]; then
        # Extract first heading as post title.
        local title=$($SED -n '/^# / { s/# //; p; q; }' "$gmi_file_path" | tr '"' "'")
        # Extract first paragraph from Gemtext
        local summary=$($SED -n '/^[A-Z]/ { p; q; }' "$gmi_file_path" | tr '"' "'")
        # Extract the date from the file name.
        local filename_date=$(basename "$gmi_file_path" | cut -d- -f1,2,3)
        local date=$($DATE --iso-8601=seconds --date "$filename_date $($DATE +%H:%M:%S)")

        cat <<META | tee "$meta_file"
local meta_date="$date"
local meta_author="$AUTHOR"
local meta_email="$EMAIL"
local meta_title="$title"
local meta_summary="$summary. .....to read on please visit my site."
META
        return
    fi

    cat "$meta_file"
}

atomfeed::_from_cache () {
    local -r gmi_file_path="$1"; shift
    local -r cache_file_path="$1"; shift

    if [ ! -f "${cache_file_path}.info" ]; then
        # No cache there.
        return 1
    elif ! diff "${cache_file_path}.info" <(ls -l "$gmi_file_path"); then
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
    fi

    local -r atom_file="$gemfeed_dir/atom.xml"
    local -r now=$($DATE --iso-8601=seconds)

    log INFO "Generating Atom feed to $atom_file"
    log INFO 'This may takes a while with an empty cache....'

    assert::not_empty now "$now"

    cat <<ATOMHEADER > "$atom_file.tmp"
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <updated>$now</updated>
    <title>$DOMAIN feed</title>
    <subtitle>$SUBTITLE</subtitle>
    <link href="gemini://$DOMAIN/gemfeed/atom.xml" rel="self" />
    <link href="gemini://$DOMAIN/" />
    <id>gemini://$DOMAIN/</id>
ATOMHEADER

    while read -r gmi_file; do
        # Load cached meta information about the post.
        source <(atomfeed::meta "$gemfeed_dir/$gmi_file")

        # Get HTML content for the feed
        local content="$(atomfeed::content "$gemfeed_dir/$gmi_file")"

        assert::not_empty meta_title "$meta_title"
        assert::not_empty meta_date "$meta_date"
        assert::not_empty meta_author "$meta_author"
        assert::not_empty meta_email "$meta_email"
        assert::not_empty meta_summary "$meta_summary"
        assert::not_empty content "$content"

        cat <<ATOMENTRY >> "$atom_file.tmp"
    <entry>
        <title>$meta_title</title>
        <link href="gemini://$DOMAIN/gemfeed/$gmi_file" />
        <id>gemini://$DOMAIN/gemfeed/$gmi_file</id>
        <updated>$meta_date</updated>
        <author>
            <name>$meta_author</name>
            <email>$meta_email</email>
        </author>
        <summary>$meta_summary</summary>
        <content type="xhtml">
            <div xmlns="http://www.w3.org/1999/xhtml">
                $content
            </div>
        </content>
    </entry>
ATOMENTRY
    done < <(gemfeed::get_posts | head -n $ATOM_MAX_ENTRIES)

    cat <<ATOMFOOTER >> "$atom_file.tmp"
</feed>
ATOMFOOTER

    if [ -n "$XMLLINT" ]; then
        log INFO 'XMLLinting Atom feed'
        $XMLLINT "$atom_file.tmp" >/dev/null ||
            log PANIC "Atom feed $atom_file.tmp isn't valid XML, please re-try"
        log INFO 'Atom feed is OK'
    fi

    # Delete the 3rd line of the atom feeds (global feed update timestamp)
    if ! diff -u <($SED 3d "$atom_file") <($SED 3d "$atom_file.tmp"); then
        log INFO 'Feed got something new!'
        mv "$atom_file.tmp" "$atom_file"
    else
        log INFO 'Nothing really new in the feed'
        rm "$atom_file.tmp"
    fi
}
