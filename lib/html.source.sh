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

    if [ -n "$text" ]; then
        echo "<span>$(html::encode "$text")</span><br />"
    else
        echo '<br />'
    fi
}

# Make a HTML header.
html::make_heading () {
    local -r text=$($SED -E 's/^#+ //' <<< "$1"); shift
    local -r level="$1"; shift
    local -r id="$(generate::internal_link_id "$text")"

    echo "<h${level} style='display: inline' id='${id}'>$(html::encode "$text")</h${level}><br />"
}

# Make a HTML quotation
html::make_quote () {
    local -r quote="${1/> }"
    echo "<span class='quote'>$(html::encode "$quote")</span><br />"
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

html::theme () {
    local -r html_base_dir="$CONTENT_BASE_DIR/html"
    log INFO "Installing theme $HTML_THEME_DIR"

    html::theme::styles "$html_base_dir"
    html::theme::webfonts "$html_base_dir"
}

html::theme::styles () {
    local -r html_base_dir="$1"; shift
    log INFO 'Installing theme CSS files'

    cp "$HTML_CSS_STYLE" "$html_base_dir/"
    while read -r section_dir; do
        local override_source="$HTML_THEME_DIR/style-$(basename "$section_dir")-override.css"
        local override_dest="$section_dir/style-override.css"
        if [ ! -f "$override_source" ]; then
            touch "$override_dest" # Empty override
        else
            cp "$override_source" "$override_dest"
        fi
    done < <(find "$html_base_dir" -mindepth 1 -maxdepth 1 -type d | $GREP -E -v '(\.git)')
}

html::theme::webfonts () {
    local -r html_base_dir="$1"; shift
    log INFO 'Installing theme webfonts'

    set +u

    if [ -f "$HTML_WEBFONT_TEXT" ]; then
        cp "$HTML_WEBFONT_TEXT" "$html_base_dir/text.ttf"
    fi

    if [ -f "$HTML_WEBFONT_HEADING" ]; then
        cp "$HTML_WEBFONT_HEADING" "$html_base_dir/heading.ttf"
    elif [ -f "$HTML_WEBFONT_TEXT" ]; then
        cp "$HTML_WEBFONT_TEXT" "$html_base_dir/heading.ttf"
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

    set -u
}

html::source_highlight () {
    local -r bare_text="$1"; shift
    local -r language="$1"; shift

    # Trim whitespace from language (handles cases like "``` ")
    local -r lang_trimmed="$($SED -E 's/^ +| +$//g' <<< "$language")"

    if [[ -z "$lang_trimmed" || -z "$SOURCE_HIGHLIGHT" ]]; then
        echo '<pre>'
        html::encode "$bare_text"
        echo '</pre>'
    else
        if [[ "$lang_trimmed" == "AUTO" ]]; then
            log WARN "GNU Source Highlight auto detection not yet supported!"
            echo '<pre>'
            html::encode "$bare_text"
            echo '</pre>'
        else
            # Build command safely to avoid empty args and word splitting
            local -a cmd=("$SOURCE_HIGHLIGHT" "--src-lang=$lang_trimmed")
            if [ -n "$SOURCE_HIGHLIGHT_CSS" ]; then
                cmd+=("--style-css-file=$SOURCE_HIGHLIGHT_CSS")
            fi
            if ! "${cmd[@]}" <<< "$bare_text" 2>/dev/null | $SED 's|<tt>||; s|</tt>||;'; then
                # Fallback if source-highlight doesn't support the language
                echo '<pre>'
                html::encode "$bare_text"
                echo '</pre>'
            fi
        fi
    fi
}

html::list::encode () {
    local text="$1"; shift

    if [[ "$text" != '⇢ '* ]]; then
        # No ToC
        html::encode "$text"
        return
    fi

    local -i toc_indent=0

    # If there's a . (dot) in the liste element, it then indicates a ToC element
    while [[ "$text" == '⇢ '* ]]; do
        text="$($SED 's/⇢ //' <<< "$text")"
        : $(( toc_indent++ ))
    done

    while [ $toc_indent -ge 2 ]; do
        echo -n '⇢ '
        : $(( toc_indent-- ))
    done

    local -r id="$(generate::internal_link_id "$text")"
    echo "<a href='#$id'>$(html::encode "$text")</a>"
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
                echo "<li>$(html::list::encode "${line/\* /}")</li>" | html::process_inline
            else
                is_list=no
                echo "</ul><br />"
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
                echo "<li>$(html::list::encode "${line/\* /}")</li>" | html::process_inline
                ;;
            '```'*)
                # Extract language after the opening backticks and trim spaces
                language=$($SED -E 's/^```\s*//; s/\s+$//' <<< "$line")
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

html::test () {
    local line='Hello world! This is a paragraph.'
    assert::equals "$(html::make_paragraph "$line")" "<span>Hello world! This is a paragraph.</span><br />"

    line=''
    assert::equals "$(html::make_paragraph "$line")" '<br />'

    line='Foo &<>& Bar!'
    assert::equals "$(html::make_paragraph "$line")" "<span>Foo &amp;&lt;&gt;&amp; Bar!</span><br />"

    line='echo foo 2>&1'
    assert::equals "$(html::make_paragraph "$line")" "<span>echo foo 2&gt;&amp;1</span><br />"

    line='# Header 1'
    local id='header-1'
    assert::equals "$(html::make_heading "$line" 1)" "<h1 style='display: inline' id='${id}'>Header 1</h1><br />"

    line='## Header 2'
    id='header-2'
    assert::equals "$(html::make_heading "$line" 2)" "<h2 style='display: inline' id='${id}'>Header 2</h2><br />"

    line='### Header 3'
    id='header-3'
    assert::equals "$(html::make_heading "$line" 3)" "<h3 style='display: inline' id='${id}'>Header 3</h3><br />"

    line='> This is a quote'
    assert::equals "$(html::make_quote "$line")" "<span class='quote'>This is a quote</span><br />"
    MASTODON_URI=''

    line='Hello world! This is a paragraph.'
    assert::equals "$(html::make_paragraph "$line")" '<span>Hello world! This is a paragraph.</span><br />'

    line=''
    assert::equals "$(html::make_paragraph "$line")" '<br />'

    line='Foo &<>& Bar!'
    assert::equals "$(html::make_paragraph "$line")" '<span>Foo &amp;&lt;&gt;&amp; Bar!</span><br />'

    line='echo foo 2>&1'
    assert::equals "$(html::make_paragraph "$line")" '<span>echo foo 2&gt;&amp;1</span><br />'

    line='> This is a quote'
    assert::equals "$(html::make_quote "$line")" "<span class='quote'>This is a quote</span><br />"

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

    # Trailing space after fence should not trigger source-highlight
    input_block='``` 
code
```'
    output_block='<pre>
code
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
