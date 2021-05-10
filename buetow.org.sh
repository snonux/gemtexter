#!/usr/bin/env bash

declare -r ARG=$1; shift
source buetow.org.conf

declare DATE=date
declare SED=sed
which gdate &>/dev/null && DATE=gdate
which gsed &>/dev/null && SED=gsed

## Test module

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

## Gemfeed module

# Filters out blog posts from other files in the gemfeed dir.
gemfeed::get_posts () {
    local -r gemfeed_dir="$CONTENT_DIR/gemtext/gemfeed"
    local -r gmi_pattern='^[0-9]{4}-[0-9]{2}-[0-9]{2}-.*\.gmi$'
    local -r draft_pattern='\.draft\.gmi$'

    ls "$gemfeed_dir" | grep -E "$gmi_pattern" | grep -E -v "$draft_pattern" | sort -r
}

# Adds the links from gemfeed/index.gmi to the main index site.
gemfeed::updatemainindex () {
    local -r index_gmi="$CONTENT_DIR/gemtext/index.gmi"
    local -r gemfeed_dir="$CONTENT_DIR/gemtext/gemfeed"

    # Remove old gemfeeds from main index
    $SED '/^=> .\/gemfeed\/[0-9].* - .*/d;' "$index_gmi" > "$index_gmi.tmp"
    # Add current gemfeeds to main index
    $SED -n '/^=> / { s| ./| ./gemfeed/|; p; }' "$gemfeed_dir/index.gmi" >> "$index_gmi.tmp"

    mv "$index_gmi.tmp" "$index_gmi"
    test "$ADD_GIT" == yes && git add "$index_gmi"
}

# This generates a index.gmi in the ./gemfeed subdir.
gemfeed::generate () {
    local -r gemfeed_dir="$CONTENT_DIR/gemtext/gemfeed"

cat <<GEMFEED > "$gemfeed_dir/index.gmi.tmp"
# $DOMAIN's Gemfeed

## $SUBTITLE

GEMFEED

    gemfeed::get_posts | while read gmi_file; do
        # Extract first heading as post title.
        local title=$($SED -n '/^# / { s/# //; p; q; }' "$gemfeed_dir/$gmi_file" | tr '"' "'")
        # Extract the date from the file name.
        local filename_date=$(basename "$gemfeed_dir/$gmi_file" | cut -d- -f1,2,3)

        echo "=> ./$gmi_file $filename_date - $title" >> "$gemfeed_dir/index.gmi.tmp"
    done

    mv "$gemfeed_dir/index.gmi.tmp" "$gemfeed_dir/index.gmi"
    test "$ADD_GIT" == yes && git add "$gemfeed_dir/index.gmi"

    gemfeed::updatemainindex
}

## Atom module

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
        local filename_date=$(basename $gmi_file_path | cut -d- -f1,2,3)
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
    html::gemini2html < <($SED '0,/^# / { /^# /!d; }' "$gmi_file_path") |
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

## HTML module

html::special () {
    $SED '
        s|\&|\&amp;|g;
        s|<|\&lt;|g;
        s|>|\&gt;|g;
    ' <<< "$@"
}

html::paragraph () {
    local -r text="$1"; shift
    test -n "$text" && echo "<p>$(html::special "$text")</p>"
}

html::heading () {
    local -r text=$($SED -E 's/^#+ //' <<< "$1"); shift
    local -r level="$1"; shift

    echo "<h${level}>$(html::special "$text")</h${level}>"
}

html::quote () {
    local -r quote="${1/> }"
    echo "<pre>$(html::special "$quote")</pre>"
}

html::img () {
    local link="$1"; shift
    local descr="$1"; shift

    if [ -z "$descr" ]; then
        echo -n "<a href=\"$link\"><img src=\"$link\" /></a>"
    else
        echo -n "<i>$descr:</i>"
        echo -n "<a href=\"$link\"><img alt=\"$descr\" title=\"$descr\" src=\"$link\" /></a>"
    fi
    echo "<br />"
}

html::link () {
    local -r line="${1/=> }"
    local link
    local descr

    while read -r token; do
        if [ -z "$link" ]; then
            link="$token"
        elif [ -z "$descr" ]; then
            descr="$token"
        else
            descr="$descr $token"
        fi
    done < <(echo "$line" | tr ' ' '\n')
    descr=$(html::special "$descr")

    if grep -E -q "$IMAGE_PATTERN" <<< "$link"; then
        html::img "$link" "$descr"
        return
    fi

    # If relative link convert .gmi to .html
    grep -F -q '://' <<< "$link" || link=${link/.gmi/.html}
    # If no description use link itself
    test -z "$descr" && descr="$link"

    echo "<a class=\"textlink\" href=\"$link\">$descr</a><br />"
}

html::gemini2html () {
    local -r gmi_file=$1
    local -i is_list=0
    local -i is_plain=0

    while IFS='' read -r line; do
        if [ $is_list -eq 1 ]; then
            if [[ "$line" == '* '* ]]; then
                echo "<li>${line/\* /}</li>"
            else
                is_list=0
                echo "</ul>"
            fi
            continue

        elif [ $is_plain -eq 1 ]; then
            if [[ "$line" == '```'* ]]; then
                echo "</pre>"
                is_plain=0
            else
                html::special "$line"
            fi
            continue
        fi

        case "$line" in
            '* '*)
                is_list=1
                echo "<ul>"
                echo "<li>${line/\* /}</li>"
                ;;
            '```'*)
                is_plain=1
                echo "<pre>"
                ;;
            '# '*)
                html::heading "$line" 1
                ;;
            '## '*)
                html::heading "$line" 2
                ;;
            '### '*)
                html::heading "$line" 3
                ;;
            '> '*)
                html::quote "$line"
                ;;
            '=> '*)
                html::link "$line"
                ;;
            *)
                html::paragraph "$line"
                ;;
        esac
    done
}

html::generate () {
    find $CONTENT_DIR/gemtext -type f -name \*.gmi |
    while read -r src; do
        local dest=${src/gemtext/html}
        dest=${dest/.gmi/.html}
        local dest_dir=$(dirname "$dest")
        test ! -d "$dest_dir" && mkdir -p "$dest_dir"

        cat header.html.part > "$dest.tmp"
        html::gemini2html < "$src" >> "$dest.tmp"
        cat footer.html.part >> "$dest.tmp"
        mv "$dest.tmp" "$dest"
        test "$ADD_GIT" == yes && git add "$dest"
    done

    # Add non-.gmi files to html dir.
    find $CONTENT_DIR/gemtext -type f | grep -E -v '(.gmi|atom.xml|.tmp)$' |
    while read -r src; do
        local dest=${src/gemtext/html}
        local dest_dir=$(dirname "$dest")

        test ! -d "$dest_dir" && mkdir -p "$dest_dir"
        cp -v "$src" "$dest"
        test "$ADD_GIT" == yes && git add "$dest"
    done

    # Add atom feed for HTML
    $SED 's|.gmi|.html|g; s|gemini://|https://|g' \
        < $CONTENT_DIR/gemtext/gemfeed/atom.xml \
        > $CONTENT_DIR/html/gemfeed/atom.xml
    test "$ADD_GIT" == yes && git add $CONTENT_DIR/html/gemfeed/atom.xml

    # Remove obsolete files from ./html/
    find $CONTENT_DIR/html -type f | while read -r src; do
        local dest=${src/.html/.gmi}
        dest=${dest/html/gemtext}
        test ! -f "$dest" && test "$ADD_GIT" == yes && git rm "$src"
    done
}

html::test () {
    local line="Hello world! This is a paragraph."
    assert::equals "$(html::paragraph "$line")" "<p>Hello world! This is a paragraph.</p>"

    line=""
    assert::equals "$(html::paragraph "$line")" ""

    line="Foo &<>& Bar!"
    assert::equals "$(html::paragraph "$line")" "<p>Foo &amp;&lt;&gt;&amp; Bar!</p>"

    line="# Header 1"
    assert::equals "$(html::heading "$line" 1)" "<h1>Header 1</h1>"

    line="## Header 2"
    assert::equals "$(html::heading "$line" 2)" "<h2>Header 2</h2>"

    line="### Header 3"
    assert::equals "$(html::heading "$line" 3)" "<h3>Header 3</h3>"

    line="> This is a quote"
    assert::equals "$(html::quote "$line")" "<pre>This is a quote</pre>"

    line="=> https://example.org"
    assert::equals "$(html::link "$line")" \
        "<a class=\"textlink\" href=\"https://example.org\">https://example.org</a><br />"

    line="=> index.gmi"
    assert::equals "$(html::link "$line")" \
        "<a class=\"textlink\" href=\"index.html\">index.html</a><br />"

    line="=> http://example.org Description of the link"
    assert::equals "$(html::link "$line")" \
        "<a class=\"textlink\" href=\"http://example.org\">Description of the link</a><br />"

    line="=> http://example.org/image.png"
    assert::equals "$(html::link "$line")" \
        "<a href=\"http://example.org/image.png\"><img src=\"http://example.org/image.png\" /></a><br />"

    line="=> http://example.org/image.png Image description"
    assert::equals "$(html::link "$line")" \
        "<i>Image description:</i><a href=\"http://example.org/image.png\"><img alt=\"Image description\" title=\"Image description\" src=\"http://example.org/image.png\" /></a><br />"
}

### MAIN module

main::help () {
    cat <<HELPHERE
$0's possible arguments:
    --feed
    --publish
    --test
    --help
HELPHERE
}

case $ARG in
    --test)
        html::test
        ;;
    --feeds)
        gemfeed::generate
        atomfeed::generate
        ;;
    --generate)
        html::test
        gemfeed::generate
        atomfeed::generate
        html::generate
        ;;
    --help|*)
        main::help
        ;;
esac

exit 0
