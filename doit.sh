#!/usr/bin/env bash

declare -r ARG=$1; shift

## Config section

declare -r DOMAIN=buetow.org
declare -r CONTENT_DIR=./content
declare -r AUTHOR="Paul Buetow"
declare -r EMAIL="comments@mx.buetow.org"

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

atom::generate () {
    local -r gemfeed_dir=$CONTENT_DIR/gemtext/gemfeed
    local -r atom=$gemfeed_dir/atom.xml
    local -r updated=$(date --iso-8601=seconds)

    cat <<ATOMHEADER > $atom.tmp
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>$DOMAIN feed</title>
    <subtitle>Putting the dot before the org!</subtitle>
    <link href="gemini://$DOMAIN/gemfeed/" rel="self" />
    <link href="gemini://$DOMAIN/" />
    <id>gemini://$DOMAIN</id>
    <updated>$updated</updated>
ATOMHEADER

    ls $gemfeed_dir | sort -r | grep '.gmi$' | while read post; do
        local title=$(sed -n '/^# / { s/# //; p; q; }' $gemfeed_dir/$post)
        local first_paragraph=$(sed -n '/^[A-Z]/ { p; q; }' $gemfeed_dir/$post)
        cat <<ATOMENTRY >> $atom.tmp
    <entry>
        <title>$title</title>
        <link href="gemini://$DOMAIN/gemfeed/$post" />
        <id>gemini://$DOMAIN/gemfeed/$post</id>
        <updated>$updated</updated>
        <summary>$first_paragraph</summary>
        <author>
            <name>$AUTHOR</name>
            <email>$EMAIL</email>
        </author>
    </entry>
ATOMENTRY
    done

    cat <<ATOMFOOTER >> $atom.tmp
</feed>
ATOMFOOTER

    mv $atom.tmp $atom
    git add $atom
}

## HTML module

html::paragraph () {
    local -r text="$1"

    if [ ! -z "$text" ]; then
        echo "<p>$text</p>"
    fi
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

    while read token; do
        if [ -z "$link" ]; then
            link="$token"
        elif [ -z "$descr" ]; then
            descr="$token"
        else
            descr="$descr $token"
        fi
    done < <(echo "$line" | tr ' ' '\n')

    egrep -q '\.(jpg|png|gif)$' <<< $link
    if [ $? -eq 0 ]; then
        html::img "$link" "$descr"
        return
    fi

    # If relative link convert .gmi to .html
    fgrep -q '://' <<< $link || link=${link/.gmi/.html}
    # If no description use link itself
    test -z "$descr" && descr="$link"

    echo "<a href=\"$link\">$descr</a><br />"
}

html::gemini2html () {
    local -r gmi_file=$1
    local -r html_file=$(sed 's/.gmi/.html/; s/gemtext/html/;' <<< $gmi_file)
    local -i is_list=0
    local -i line_nr
    local -i is_plain=0
    local -i plain_start

    while IFS='' read line; do
        let line_nr++

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
                local -i plain_end=$[ line_nr - 1 ]
                # Use sed, as escaping \ in bash strings is hell!
                sed -n ${plain_start},${plain_end}p $gmi_file
                echo "</pre>"
                is_plain=0
            fi
            continue
        fi

        case "$line" in
            '* '*)
                is_list=1
                echo "<ul>"
                ;;
            '```'*)
                is_plain=1
                plain_start=$[ line_nr + 1 ]
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
    done < $gmi_file
}

html::generate () {
    find $CONTENT_DIR/gemtext -type f -name \*.gmi | while read src; do
        local dest=${src/gemtext/html}
        dest=${dest/.gmi/.html}
        local dest_dir=$(dirname $dest)
        test ! -d $dest_dir && mkdir -p $dest_dir
        cat $CONTENT_DIR/header.html > $dest.tmp
        html::gemini2html $src >> $dest.tmp
        cat $CONTENT_DIR/footer.html >> $dest.tmp
        mv $dest.tmp $dest
        git add $dest
    done

    # Add non-.gmi files to html dir.
    find $CONTENT_DIR/gemtext -type f | egrep -v '(.gmi|atom.xml)$' | while read src; do
        local dest=${src/gemtext/html}
        local dest_dir=$(dirname $dest)
        test ! -d $dest_dir && mkdir -p $dest_dir
        cp -v $src $dest
        git add $dest
    done

    # Add atom feed for HTML
    sed 's|.gmi|.html|g; s|gemini://|http://|g' \
        < $CONTENT_DIR/gemtext/gemfeed/atom.xml \
        > $CONTENT_DIR/html/gemfeed/atom.xml

    # Remove obsolete files from ./html/
    find $CONTENT_DIR/html -type f | while read src; do
        local dest=${src/.html/.gmi}
        dest=${dest/html/gemtext}
        test ! -f $dest && git rm $src
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

    line="=> http://example.org"
    assert::equals "$(html::link "$line")" \
        "<a href=\"http://example.org\">http://example.org</a><br />"

    line="=> index.gmi"
    assert::equals "$(html::link "$line")" \
        "<a href=\"index.html\">index.html</a><br />"

    line="=> http://example.org Description of the link"
    assert::equals "$(html::link "$line")" \
        "<a href=\"http://example.org\">Description of the link</a><br />"

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
        ;;
    --help|*)
        main::help
        ;;
esac
