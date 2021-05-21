# Make a Markdown image.
md::make_img () {
    local link="$1"; shift
    local descr="$1"; shift

    if [ -z "$descr" ]; then
        echo "[![$link]($link)]($link)  "
    else
        echo "[![$descr]($link \"$descr\")]($link)  "
    fi
}

# Make a Markdown hyperlink.
md::make_link () {
    local link="$1"; shift
    local descr="$1"; shift

    if ! $GREP -F -q '://' <<< "$link"; then
        link=${link/.gmi/.md}
    fi
    if [[ -z "$descr" ]]; then
        descr="$link"
    fi

    echo "[$descr]($link)  "
}

# Convert Gemtext to Markdown.
md::fromgmi () {
    while IFS='' read -r line; do
        case "$line" in
            '=> '*)
                generate::make_link md "$line"
                ;;
            *)
                echo "$line"
                ;;
        esac
    done
}

# Test the Markdown package.
md::test () {
    local line='=> https://example.org'
    assert::equals "$(generate::make_link md "$line")" \
        '[https://example.org](https://example.org)  '

    line='=> index.md'
    assert::equals "$(generate::make_link md "$line")" \
        '[index.md](index.md)  '

    line='=> http://example.org Description of the link'
    assert::equals "$(generate::make_link md "$line")" \
        '[Description of the link](http://example.org)  '

    line='=> http://example.org/image.png'
    assert::equals "$(generate::make_link md "$line")" \
        '[![http://example.org/image.png](http://example.org/image.png)](http://example.org/image.png)  '

    line='=> http://example.org/image.png Image description'
    assert::equals "$(generate::make_link md "$line")" \
        '[![Image description](http://example.org/image.png "Image description")](http://example.org/image.png)  '
}
