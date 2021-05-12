atomfeed::meta () {
    local -r gmi_file_path="$1"; shift
    local -r meta_file=$($SED 's|gemtext|meta|; s|.gmi$|.meta|;' <<< "$gmi_file_path")

    local is_draft=no
    if grep -E -q '\.draft\.meta$' <<< "$meta_file"; then
        is_draft=yes
    fi

    local -r meta_dir=$(dirname "$meta_file")
    test ! -d "$meta_dir" && mkdir -p "$meta_dir"

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
        test $is_draft == no && git add "$meta_file"
        return
    fi

    cat "$meta_file"
    test $is_draft == yes && rm "$meta_file"
}

atomfeed::content () {
    local -r gmi_file_path="$1"; shift
    # sed: Remove all before the first header
    # sed: Make HTML links absolute, Atom relative URLs feature seems a mess
    # across different Atom clients.
    html::fromgmi < <($SED '0,/^# / { /^# /!d; }' "$gmi_file_path") |
    $SED "
        s|href=\"\./|href=\"https://$DOMAIN/gemfeed/|g;
        s|src=\"\./|src=\"https://$DOMAIN/gemfeed/|g;
    "
}

atomfeed::generate () {
    local -r gemfeed_dir="$CONTENT_DIR/gemtext/gemfeed"
    local -r atom_file="$gemfeed_dir/atom.xml"
    local -r now=$($DATE --iso-8601=seconds)

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

    # Delete the 3rd line of the atom feeds (global feed update timestamp)
    if ! diff -u <($SED 3d "$atom_file") <($SED 3d "$atom_file.tmp"); then
        echo "Feed got something new!"
        mv "$atom_file.tmp" "$atom_file"
        test "$ADD_GIT" == yes && git add "$atom_file"
    else
        echo "Nothing really new in the feed"
        rm "$atom_file.tmp"
    fi
}
