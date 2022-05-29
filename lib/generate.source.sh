# Generate a HTML or Markdown link from given Gemtext link.
generate::make_link () {
    local -r what="$1"; shift
    local -r line="${1/=> }"; shift
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

    if $GREP -E -q "$IMAGE_PATTERN" <<< "$link"; then
        if [[ "$what" == md ]]; then
            md::make_img "$link" "$descr"
        else
            html::make_img "$link" "$(html::encode "$descr")"
        fi
        return
    fi

    if [[ "$what" == md ]]; then
        md::make_link "$link" "$descr"
    else
        html::make_link "$link" "$(html::encode "$descr")"
    fi
}

# Add other docs (e.g. images, videos) from Gemtext to output format.
generate::fromgmi_add_docs () {
    local -r src="$1"; shift
    local -r format="$1"; shift
    local -r dest=${src/gemtext/$format}
    local -r dest_dir=$(dirname "$dest")

    if [[ ! -d "$dest_dir" ]]; then
        mkdir -p "$dest_dir"
    fi
    cp "$src" "$dest"
}

# Remove docs from output format which aren't present in Gemtext anymore.
generate::fromgmi_cleanup_docs () {
    local -r src="$1"; shift
    local -r format="$1"; shift
    local dest=${src/.$format/.gmi}
    dest=${dest/$format/gemtext}

    if [[ ! -f "$dest" ]]; then
        rm "$src"
    fi
}

# Convert the Gemtext Atom feed to a HTML Atom feed.
generate::convert_gmi_atom_to_html_atom () {
    local -r format="$1"; shift
    if [[ "$format" != html ]]; then
        return
    fi

    log INFO 'Converting Gemtext Atom feed to HTML Atom feed'

    $SED 's|.gmi|.html|g; s|gemini://|https://|g' \
        < $CONTENT_BASE_DIR/gemtext/gemfeed/atom.xml \
        > $CONTENT_BASE_DIR/html/gemfeed/atom.xml
}

# Internal helper function for generate::fromgmi
generate::_fromgmi () {
    local -r src="$1"; shift
    local -r format="$1"; shift
    local dest=${src/gemtext/$format}
    dest=${dest/.gmi/.$format}
    local dest_dir=$(dirname "$dest")

    if [[ ! -d "$dest_dir" ]]; then
        mkdir -p "$dest_dir"
    fi

    if [[ "$format" == html ]]; then
        cat "$HTML_HEADER" > "$dest.tmp"
        html::fromgmi < "$src" >> "$dest.tmp"
        cat "$HTML_FOOTER" >> "$dest.tmp"

    elif [[ "$format" == md ]]; then
        md::fromgmi < "$src" >> "$dest.tmp"
    fi

    local title=$($SED -n '/^# / { s/# //; p; q; }' "$src" | tr '"' "'")
    if [[ -z "$title" ]]; then
        title=$SUBTITLE
    fi

    if [[ "$format" == html ]]; then
        local stylesheet="$(basename "$HTML_CSS_STYLE")"
        local stylesheet_override="${stylesheet/.css/-override.css}"
        if [[ "$CONTENT_BASE_DIR/html" != "$(dirname "$dest")" ]]; then
            stylesheet="../$stylesheet"
        fi
        $SED -i "s|%%TITLE%%|$title|g;
                 s|%%DOMAIN%%|$DOMAIN|g;
                 s|%%STYLESHEET%%|$stylesheet|g;
                 s|%%STYLESHEET_OVERRIDE%%|$stylesheet_override|g;" "$dest.tmp"
        mv "$dest.tmp" "$dest"
    fi
}

# Generate a given output format from a Gemtext file.
generate::fromgmi () {
    local -i num_gmi_files=0
    local -i num_doc_files=0

    log INFO "Generating $* from Gemtext"

    while read -r src; do
        num_gmi_files=$(( num_gmi_files + 1 ))
        log INFO "Generating output formats from $src"
        for format in "$@"; do
            generate::_fromgmi "$src" "$format" &
        done
    done < <(find "$CONTENT_BASE_DIR/gemtext" -type f -name \*.gmi)
    wait

    log INFO "Converted $num_gmi_files Gemtext files"

    # Add HTML extras (will be cleaned up further below)
    cp $HTML_CSS_STYLE $CONTENT_BASE_DIR/gemtext/style.css
    for section in . gemfeed notes; do
        if [[ ! -d "$CONTENT_BASE_DIR/gemtext/$section" ]]; then
            continue
        fi

        local override_source="./htmlextras/style-${section}-override.css"
        local override_dest="$CONTENT_BASE_DIR/gemtext/$section/style-override.css"
        if [ ! -f "$override_source" ]; then
            touch "$override_dest" # Empty override
            continue
        fi
        cp "$override_source" "$override_dest"
    done
    cp "$HTML_WEBFONT_TEXT" $CONTENT_BASE_DIR/gemtext/text.ttf
    cp "$HTML_WEBFONT_CODE" $CONTENT_BASE_DIR/gemtext/code.ttf
    cp "$HTML_WEBFONT_HANDNOTES" $CONTENT_BASE_DIR/gemtext/handnotes.ttf
    cp "$HTML_WEBFONT_TYPEWRITER" $CONTENT_BASE_DIR/gemtext/typewriter.ttf

    # Add non-.gmi files to html dir.
    log VERBOSE "Adding other docs to $*"

    while read -r src; do
        num_doc_files=$(( num_doc_files + 1 ))
        for format in "$@"; do
            generate::fromgmi_add_docs "$src" "$format" &
        done
    done < <(find "$CONTENT_BASE_DIR/gemtext" -type f | $GREP -E -v '(\.git.*|\.gmi|atom.xml|\.tmp|htmlextras)$')
    wait

    log INFO "Added $num_doc_files other documents to each of $*"

    # Add atom feed for HTML
    generate::convert_gmi_atom_to_html_atom 'html' &

    # Remove obsolete files from ./html/.
    # Note: The _config.yml is the config file for GitHub pages (md format).
    # Anoter note: The CNAME file is required by GitHub pages as well for custom domains.
    for format in "$@"; do
        find "$CONTENT_BASE_DIR/$format" -type f |
        $GREP -E -v '(\.git.*|_config.yml|CNAME|.domains|robots.txt|static)$'|
        while read -r src; do
            generate::fromgmi_cleanup_docs "$src" "$format" 
        done &
    done
    wait

    # Cleanup HTML extras
    rm $CONTENT_BASE_DIR/gemtext/{style.css,*.ttf}

    for format in "$@"; do
        log INFO "$format can be found in $CONTENT_BASE_DIR/$format now"
    done
    log INFO "You may want to commit all changes to version control!"
}
