md::make_img () {
    local link="$1"; shift
    local descr="$1"; shift

    if [ -z "$descr" ]; then
        echo "[![$link]($link)]($link)  "
    else
        echo "[![$descr]($link \"$descr\")]($link)  "
    fi
}

md::make_link () {
    local link="$1"; shift
    local descr="$1"; shift

    grep -F -q '://' <<< "$link" || link=${link/.gmi/.md}
    test -z "$descr" && descr="$link"

    echo "[$descr]($link)  "
}

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
