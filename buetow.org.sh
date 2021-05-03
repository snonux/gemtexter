#!/usr/bin/env bash

declare -r ARG=$1; shift

source buetow.org.conf

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

## Atom module

atom::meta () {
    local -r now="$1"; shift
    local -r gmi_file_path="$1"; shift
    local -r meta_file=$(sed 's|gemtext|meta|; s|.gmi$|.meta|;' <<< "$gmi_file_path")

    local -r meta_dir=$(dirname "$meta_file")
    test ! -d "$meta_dir" && mkdir -p "$meta_dir"

    if [ ! -f "$meta_file" ]; then
        # Extract first heading as post title.
        local title=$(sed -n '/^# / { s/# //; p; q; }' "$gmi_file_path" | tr '"' "'")
        # Extract first paragraph from Gemtext
        local summary=$(sed -n '/^[A-Z]/ { p; q; }' "$gmi_file_path" | tr '"' "'")

        cat <<META | tee "$meta_file"
local meta_date="$now"
local meta_author="$AUTHOR"
local meta_email="$EMAIL"
local meta_title="$title"
local meta_summary="$summary. .....to read on please visit my site."
META
        git add "$meta_file"
        return
    fi

    cat "$meta_file"
}

atom::generate () {
    local -r gemfeed_dir="$CONTENT_DIR/gemtext/gemfeed"
    local -r atom_file="$gemfeed_dir/atom.xml"
    local -r now=$(date --iso-8601=seconds)

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
        source <(atom::meta "$now" "$gemfeed_dir/$gmi_file")

        cat <<ATOMENTRY >> "$atom_file.tmp"
    <entry>
        <title>$meta_title</title>
        <link href="gemini://$DOMAIN/gemfeed/$gmi_file" />
        <id>gemini://$DOMAIN/gemfeed/$gmi_file</id>
        <updated>$meta_date</updated>
        <summary>$meta_summary</summary>
        <author>
            <name>$meta_author</name>
            <email>$meta_email</email>
        </author>
    </entry>
ATOMENTRY
    done < <(ls "$gemfeed_dir" | sort -r | grep '.gmi$' | head -n $ATOM_MAX_ENTRIES)

    cat <<ATOMFOOTER >> "$atom_file.tmp"
</feed>
ATOMFOOTER

    # Delete the 3rd line of the atom feeds (global feed update timestamp)
    if ! diff -u <(sed 3d "$atom_file.tmp") <(sed 3d "$atom_file"); then
        echo "Feed got something new!"
        mv "$atom_file.tmp" "$atom_file"
        git add "$atom_file"
    else
        echo "Nothing really new in the feed"
        rm "$atom_file.tmp"
    fi
}

## HTML module

html::paragraph () {
    local -r text="$1"
    test -n "$text" && echo "<p>$text</p>"
}

html::heading () {
    local -r text=$(sed -E 's/^#+ //' <<< "$1")
    local -r level="$2"

    echo "<h${level}>$text</h${level}>"
}

html::quote () {
    local -r quote="${1/> }"
    echo "<pre>$quote</pre>"
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
                echo "$line" | sed 's|<|\&lt;|g; s|>|\&gt;|g'
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
    done < "$gmi_file"
}

html::generate () {
    find $CONTENT_DIR/gemtext -type f -name \*.gmi |
    while read -r src; do
        local dest=${src/gemtext/html}
        dest=${dest/.gmi/.html}
        local dest_dir=$(dirname "$dest")
        test ! -d "$dest_dir" && mkdir -p "$dest_dir"
        cat header.html.part > "$dest.tmp"
        html::gemini2html "$src" >> "$dest.tmp"
        cat footer.html.part >> "$dest.tmp"
        mv "$dest.tmp" "$dest"
        git add "$dest"
    done

    # Add non-.gmi files to html dir.
    find $CONTENT_DIR/gemtext -type f | grep -E -v '(.gmi|atom.xml|.tmp)$' |
    while read -r src; do
        local dest=${src/gemtext/html}
        local dest_dir=$(dirname "$dest")
        test ! -d "$dest_dir" && mkdir -p "$dest_dir"
        cp -v "$src" "$dest"
        git add "$dest"
    done

    # Add atom feed for HTML
    sed 's|.gmi|.html|g; s|gemini://|https://|g' \
        < $CONTENT_DIR/gemtext/gemfeed/atom.xml \
        > $CONTENT_DIR/html/gemfeed/atom.xml
    git add $CONTENT_DIR/html/gemfeed/atom.xml

    # Remove obsolete files from ./html/
    find $CONTENT_DIR/html -type f | while read -r src; do
        local dest=${src/.html/.gmi}
        dest=${dest/html/gemtext}
        test ! -f "$dest" && git rm "$src"
    done
}

html::test () {
    local line="Hello world! This is a paragraph."
    assert::equals "$(html::paragraph "$line")" "<p>Hello world! This is a paragraph.</p>"

    line=""
    assert::equals "$(html::paragraph "$line")" ""

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
    --atom
    --publish
    --test
    --help
HELPHERE
}

case $ARG in
    --test)
        html::test
        ;;
    --atom)
        atom::generate
        ;;
    --publish)
        html::test
        atom::generate
        html::generate
        # git commit -a
        ;;
    --help|*)
        main::help
        ;;
esac
