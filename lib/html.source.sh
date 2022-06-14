# Convert special characters to their HTML codes
html::encode () {
    $SED '
        s|\&|\&amp;|g;
        s|<|\&lt;|g;
        s|>|\&gt;|g;
    ' <<< "$@"
}

# Make a HTML paragraph.
html::make_paragraph () {
    local -r text="$1"; shift

    if [[ -n "$text" ]]; then
        echo "<p>$(html::encode "$text")</p>"
    fi
}

# Make a HTML header.
html::make_heading () {
    local -r text=$($SED -E 's/^#+ //' <<< "$1"); shift
    local -r level="$1"; shift
    echo "<h${level}>$(html::encode "$text")</h${level}>"
}

# Make a HTML quotation
html::make_quote () {
    local -r quote="${1/> }"
    echo "<p class=\"quote\"><i>$(html::encode "$quote")</i></p>"
}

# Make a HTML image
html::make_img () {
    local link="$1"; shift
    local descr="$1"; shift

    if [ -z "$descr" ]; then
        echo -n "<a href=\"$link\"><img src=\"$link\" /></a>"
    else
        echo -n "<a href=\"$link\"><img alt=\"$descr\" title=\"$descr\" src=\"$link\" /></a>"
    fi

    echo "<br />"
}

# Make a HTML hyperlink
html::make_link () {
    local link="$1"; shift
    local descr="$1"; shift

    if ! $GREP -F -q '://' <<< "$link"; then
        link=${link/.gmi/.html}
    fi

    if [[ -z "$descr" ]]; then
        descr="$link"
    fi

    echo "<a class=\"textlink\" href=\"$link\">$descr</a><br />"
}

# Make inline code!
html::process_inline_code () {
    $SED -E 's|`([^`]+)`|<span class="inlinecode">\1</span>|g'
}

html::process_inline () {
    # As of now we only inlinde "code blocks", but we can chain more here later!
    html::process_inline_code
}

# Convert Gemtext to HTML
html::fromgmi () {
    local is_list=no
    local is_plain=no

    while IFS='' read -r line; do
        if [[ "$is_list" == yes ]]; then
            if [[ "$line" == '* '* ]]; then
                echo "<li>$(html::encode "${line/\* /}")</li>"
            else
                is_list=no
                echo "</ul>"
            fi
            continue

        elif [[ "$is_plain" == yes ]]; then
            if [[ "$line" == '```'* ]]; then
                echo "</pre><br />"
                is_plain=no
            else
                html::encode "$line"
            fi
            continue
        fi

        case "$line" in
            '* '*)
                is_list=yes
                echo "<ul>"
                echo "<li>$(html::encode "${line/\* /}")</li>" |
                    html::process_inline
                ;;
            '```'*)
                is_plain=yes
                echo '<pre>'
                ;;
            '# '*)
                html::make_heading "$line" 1 | html::process_inline
                ;;
            '## '*)
                html::make_heading "$line" 2 | html::process_inline
                ;;
            '### '*)
                html::make_heading "$line" 3 | html::process_inline
                ;;
            '> '*)
                html::make_quote "$line" | html::process_inline
                ;;
            '=> '*)
                generate::make_link html "$line" | html::process_inline
                ;;
            *)
                if [[ "$is_plain" == no ]]; then
                    html::make_paragraph "$line" | html::process_inline
                else
                    html::make_paragraph "$line"
                fi
                ;;
        esac
    done
}

# Test HTML package.
html::test () {
    local line='Hello world! This is a paragraph.'
    assert::equals "$(html::make_paragraph "$line")" '<p>Hello world! This is a paragraph.</p>'

    line=''
    assert::equals "$(html::make_paragraph "$line")" ''

    line='Foo &<>& Bar!'
    assert::equals "$(html::make_paragraph "$line")" '<p>Foo &amp;&lt;&gt;&amp; Bar!</p>'

    line='echo foo 2>&1'
    assert::equals "$(html::make_paragraph "$line")" '<p>echo foo 2&gt;&amp;1</p>'

    line='# Header 1'
    assert::equals "$(html::make_heading "$line" 1)" '<h1>Header 1</h1>'

    line='## Header 2'
    assert::equals "$(html::make_heading "$line" 2)" '<h2>Header 2</h2>'

    line='### Header 3'
    assert::equals "$(html::make_heading "$line" 3)" '<h3>Header 3</h3>'

    line='> This is a quote'
    assert::equals "$(html::make_quote "$line")" '<p class="quote"><i>This is a quote</i></p>'

    line='Testing: `hello_world.sh --debug` :-) `another one`!'
    assert::equals "$(echo "$line" | html::process_inline_code)" \
        'Testing: <span class="inlinecode">hello_world.sh --debug</span> :-) <span class="inlinecode">another one</span>!'

    line='=> https://example.org'
    assert::equals "$(generate::make_link html "$line")" \
        '<a class="textlink" href="https://example.org">https://example.org</a><br />'

    line='=> index.html'
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
        '<a href="http://example.org/image.png"><img alt="Image description" title="Image description" src="http://example.org/image.png" /></a><br />'
}
