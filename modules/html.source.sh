html::special () {
    $SED '
        s|\&|\&amp;|g;
        s|<|\&lt;|g;
        s|>|\&gt;|g;
    ' <<< "$@"
}

html::make_paragraph () {
    local -r text="$1"; shift
    test -n "$text" && echo "<p>$(html::special "$text")</p>"
}

html::make_heading () {
    local -r text=$($SED -E 's/^#+ //' <<< "$1"); shift
    local -r level="$1"; shift

    echo "<h${level}>$(html::special "$text")</h${level}>"
}

html::make_quote () {
    local -r quote="${1/> }"
    echo "<pre>$(html::special "$quote")</pre>"
}

html::make_img () {
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

html::make_link () {
    local link="$1"; shift
    local descr="$1"; shift

    grep -F -q '://' <<< "$link" || link=${link/.gmi/.html}
    test -z "$descr" && descr="$link"
    echo "<a class=\"textlink\" href=\"$link\">$descr</a><br />"
}

html::fromgmi () {
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
                html::make_heading "$line" 1
                ;;
            '## '*)
                html::make_heading "$line" 2
                ;;
            '### '*)
                html::make_heading "$line" 3
                ;;
            '> '*)
                html::make_quote "$line"
                ;;
            '=> '*)
                generate::make_link html "$line"
                ;;
            *)
                html::make_paragraph "$line"
                ;;
        esac
    done
}

html::test () {
    local line='Hello world! This is a paragraph.'
    assert::equals "$(html::make_paragraph "$line")" '<p>Hello world! This is a paragraph.</p>'

    line=''
    assert::equals "$(html::make_paragraph "$line")" ''

    line='Foo &<>& Bar!'
    assert::equals "$(html::make_paragraph "$line")" '<p>Foo &amp;&lt;&gt;&amp; Bar!</p>'

    line='# Header 1'
    assert::equals "$(html::make_heading "$line" 1)" '<h1>Header 1</h1>'

    line='## Header 2'
    assert::equals "$(html::make_heading "$line" 2)" '<h2>Header 2</h2>'

    line='### Header 3'
    assert::equals "$(html::make_heading "$line" 3)" '<h3>Header 3</h3>'

    line='> This is a quote'
    assert::equals "$(html::make_quote "$line")" '<pre>This is a quote</pre>'

    line='=> https://example.org'
    assert::equals "$(generate::make_link html "$line")" \
        '<a class="textlink" href="https://example.org">https://example.org</a><br />'

    line='=> index.gmi'
    assert::equals "$(generate::make_link html "$line")" \
        '<a class="textlink" href="index.html">index.html</a><br />'

    line='=> http://example.org Description of the link'
    assert::equals "$(generate::make_link html "$line")" \
        '<a class="textlink" href="http://example.org">Description of the link</a><br />'

    line='=> http://example.org/image.png'
    assert::equals "$(generate::make_link html "$line")" \
        '<a href="http://example.org/image.png"><img src="http://example.org/image.png" /></a><br />'

    line='=> http://example.org/image.png Image description'
    assert::equals "$(generate::make_link html "$line")" \
        '<i>Image description:</i><a href="http://example.org/image.png"><img alt="Image description" title="Image description" src="http://example.org/image.png" /></a><br />'
}
