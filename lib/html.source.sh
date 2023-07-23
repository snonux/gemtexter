# Convert specia characters to their HTML codes
html::encode () {
    $SED '
        s|\&|\&amp;|g;
        s|<|\&lt;|g;
        s|>|\&gt;|g;
        s|'\''|\&#39;|g;
    ' <<< "$@"
}

# Make a HTML paragraph.
html::make_paragraph () {
    local -r text="$1"; shift

    if [ "$HTML_VARIANT_TO_USE" = exact ]; then
        if [ -n "$text" ]; then
            echo "<span>$(html::encode "$text")</span><br />"
        else
            echo '<br />'
        fi
    elif [ -n "$text" ]; then
        echo "<p>$(html::encode "$text")</p>"
    fi
}

# Make a HTML header.
html::make_heading () {
    local -r text=$($SED -E 's/^#+ //' <<< "$1"); shift
    local -r level="$1"; shift

    if [ "$HTML_VARIANT_TO_USE" = exact ]; then
        #echo "<span class='h${level}'>$(html::encode "$text")</span><br />"
        echo "<h${level} style='display: inline'>$(html::encode "$text")</h${level}><br />"
    else
        echo "<h${level}>$(html::encode "$text")</h${level}><br />"
    fi
}

# Make a HTML quotation
html::make_quote () {
    local -r quote="${1/> }"
    if [ "$HTML_VARIANT_TO_USE" = exact ]; then
        echo "<span class='quote'>$(html::encode "$quote")</span><br />"
    else
        echo "<p class='quote'><i>$(html::encode "$quote")</i></p>"
    fi
}

# Make a HTML image
html::make_img () {
    local link="$1"; shift
    local descr="$1"; shift

    if [ -z "$descr" ]; then
        echo "<a href='$link'><img src='$link' /></a><br />"
    else
        echo "<a href='$link'><img alt='$descr' title='$descr' src='$link' /></a><br />"
    fi
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

    local mastodon_verify=''
    if [[ "$link" = "$MASTODON_URI" ]]; then
        mastodon_verify=" rel='me'"
    fi

    echo "<a class='textlink' href='$(html::encode "$link")'$mastodon_verify>$descr</a><br />"
}

html::process_inline () {
    $SED -E "s|\`([^\`]+)\`|<span class='inlinecode'>\\1</span>|g"
}

html::add_extras () {
    local -r html_base_dir="$CONTENT_BASE_DIR/html"
    cp "$HTML_CSS_STYLE" "$html_base_dir/style.css"

    while read -r section_dir; do
        local override_source="./extras/html/style-$(basename "$section_dir")-override.css"
        local override_dest="$section_dir/style-override.css"
        if [ ! -f "$override_source" ]; then
            touch "$override_dest" # Empty override
        else
            cp "$override_source" "$override_dest"
        fi
    done < <(find "$html_base_dir" -mindepth 1 -maxdepth 1 -type d | $GREP -E -v '(\.git)')

    if [ -f "$HTML_WEBFONT_TEXT" ]; then
        cp "$HTML_WEBFONT_TEXT" "$html_base_dir/text.ttf"
    fi
    if [ -f "$HTML_WEBFONT_CODE" ]; then
        cp "$HTML_WEBFONT_CODE" "$html_base_dir/code.ttf"
    fi
    if [ -f "$HTML_WEBFONT_HANDNOTES" ]; then
        cp "$HTML_WEBFONT_HANDNOTES" "$html_base_dir/handnotes.ttf"
    fi
    if [ -f "$HTML_WEBFONT_TYPEWRITER" ]; then
        cp "$HTML_WEBFONT_TYPEWRITER" "$html_base_dir/typewriter.ttf"
    fi
}

html::source_highlight () {
    local -r bare_text="$1"; shift
    local -r language="$1"; shift

    if [[ -z "$language" || -z "$SOURCE_HIGHLIGHT" ]]; then
        echo '<pre>'
        html::encode "$bare_text"
        echo '</pre>'
    else
        $SOURCE_HIGHLIGHT --src-lang="$language" <<< "$bare_text" |
            $SED 's|<tt>||; s|</tt>||;'
    fi
}

# Convert Gemtext to HTML
html::fromgmi () {
    local is_list=no
    local is_bare=no
    local bare_text=''
    local language=''

    while IFS='' read -r line; do
        if [[ "$is_list" == yes ]]; then
            if [[ "$line" == '* '* ]]; then
                echo "<li>$(html::encode "${line/\* /}")</li>" |
                    html::process_inline
            else
                is_list=no
                if [ "$HTML_VARIANT_TO_USE" = exact ]; then
                    echo "</ul><br />"
                else
                    echo "</ul>"
                fi
            fi
            continue

        elif [[ "$is_bare" == yes ]]; then
            if [[ "$line" == '```'* ]]; then
                html::source_highlight "$bare_text" "$language"
                is_bare=no
                bare_text=''
                language=''
            elif [ -z "$bare_text" ]; then
                bare_text="$line"
            else
                bare_text="$bare_text
$line"
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
                language=$(cut -d'`' -f4 <<< "$line")
                is_bare=yes
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
                html::make_paragraph "$line" | html::process_inline
                ;;
        esac
    done
}

# Test default HTML variant.
html::test::default () {
    MASTODON_URI=''

    local line='Hello world! This is a paragraph.'
    assert::equals "$(html::make_paragraph "$line")" '<p>Hello world! This is a paragraph.</p>'

    line=''
    assert::equals "$(html::make_paragraph "$line")" ''

    line='Foo &<>& Bar!'
    assert::equals "$(html::make_paragraph "$line")" '<p>Foo &amp;&lt;&gt;&amp; Bar!</p>'

    line='echo foo 2>&1'
    assert::equals "$(html::make_paragraph "$line")" '<p>echo foo 2&gt;&amp;1</p>'

    line='> This is a quote'
    assert::equals "$(html::make_quote "$line")" "<p class='quote'><i>This is a quote</i></p>"

    line='Testing: `hello_world.sh --debug` :-) `another one`!'
    assert::equals "$(echo "$line" | html::process_inline)" \
        "Testing: <span class='inlinecode'>hello_world.sh --debug</span> :-) <span class='inlinecode'>another one</span>!"

    line='=> https://example.org'
    assert::equals "$(generate::make_link html "$line")" \
        "<a class='textlink' href='https://example.org'>https://example.org</a><br />"

    line="=> https://example.org/foo'bar"
    assert::equals "$(generate::make_link html "$line")" \
        "<a class='textlink' href='https://example.org/foo&#39;bar'>https://example.org/foo'bar</a><br />"

    line='=> index.html'
    assert::equals "$(generate::make_link html "$line")" \
        "<a class='textlink' href='index.html'>index.html</a><br />"

    line='=> http://example.org Description of the link'
    assert::equals "$(generate::make_link html "$line")" \
        "<a class='textlink' href='http://example.org'>Description of the link</a><br />"

    # Test Mastodon verification.
    MASTODON_URI='https://fosstodon.org/@snonux'
    line='=> https://fosstodon.org/@snonux Me at Mastodon'
    assert::equals "$(generate::make_link html "$line")" \
        "<a class='textlink' href='https://fosstodon.org/@snonux' rel='me'>Me at Mastodon</a><br />"
    MASTODON_URI=''

    line='=> http://example.org/image.png'
    assert::equals "$(generate::make_link html "$line")" \
        "<a href='http://example.org/image.png'><img src='http://example.org/image.png' /></a><br />"

    line='=> http://example.org/image.png Image description'
    assert::equals "$(generate::make_link html "$line")" \
        "<a href='http://example.org/image.png'><img alt='Image description' title='Image description' src='http://example.org/image.png' /></a><br />"


    local input_block='```
this
    is
      a
       bare block
```'

    local output_block='<pre>
this
    is
      a
       bare block
</pre>'

    assert::equals "$(html::fromgmi <<< "$input_block")" "$output_block"

    if [ -n "$SOURCE_HIGHLIGHT" ]; then
        input_block='```bash
if [ -z $foo ]; then
    echo $foo
fi
```'
        assert::contains "$(html::fromgmi <<< "$input_block")" 'GNU source-highlight'
    fi
}

# Test exact HTML variant.
html::test::exact () {
    local line='Hello world! This is a paragraph.'
    assert::equals "$(html::make_paragraph "$line")" "<span>Hello world! This is a paragraph.</span><br />"

    line=''
    assert::equals "$(html::make_paragraph "$line")" '<br />'

    line='Foo &<>& Bar!'
    assert::equals "$(html::make_paragraph "$line")" "<span>Foo &amp;&lt;&gt;&amp; Bar!</span><br />"

    line='echo foo 2>&1'
    assert::equals "$(html::make_paragraph "$line")" "<span>echo foo 2&gt;&amp;1</span><br />"

    line='# Header 1'
    assert::equals "$(html::make_heading "$line" 1)" "<h1 style='display: inline'>Header 1</h1><br />"

    line='## Header 2'
    assert::equals "$(html::make_heading "$line" 2)" "<h2 style='display: inline'>Header 2</h2><br />"

    line='### Header 3'
    assert::equals "$(html::make_heading "$line" 3)" "<h3 style='display: inline'>Header 3</h3><br />"

    line='> This is a quote'
    assert::equals "$(html::make_quote "$line")" "<span class='quote'>This is a quote</span><br />"
}

html::test () {
    HTML_VARIANT_TO_USE=default html::test::default
    HTML_VARIANT_TO_USE=exact html::test::exact
}
