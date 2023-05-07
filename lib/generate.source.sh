# Generate a HTML or Markdown link from given Gemtext link.
generate::make_link () {
    local -r what="$1"; shift
    local -r line="${1/=> }"; shift
    local link=''
    local descr=''

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

    if [ ! -f "$CONTENT_BASE_DIR/gemtext/gemfeed/atom.xml" ]; then
        return
    fi

    log INFO 'Converting Gemtext Atom feed to HTML Atom feed'

    if [ ! -d "$CONTENT_BASE_DIR/html/gemfeed" ]; then
        mkdir -p "$CONTENT_BASE_DIR/html/gemfeed"
    fi

    $SED 's|.gmi |.html |g; s|.gmi"|.html"|g; s|.gmi</id>|.html</id>|g; s|gemini://|https://|g' \
        < "$CONTENT_BASE_DIR/gemtext/gemfeed/atom.xml" \
        > "$CONTENT_BASE_DIR/html/gemfeed/atom.xml.tmp"

    atomfeed::xmllint "$CONTENT_BASE_DIR/html/gemfeed/atom.xml.tmp" &&
    mv "$CONTENT_BASE_DIR/html/gemfeed/atom.xml.tmp" "$CONTENT_BASE_DIR/html/gemfeed/atom.xml"
}

# Internal helper function for generate::fromgmi
generate::_to_output_format () {
    local -r src="$1"; shift
    local -r format="$1"; shift

    local dest=${src/gemtext/$format}
    dest=${dest/.gmi/.$format}
    local dest_dir=$(dirname "$dest")

    local title=$($SED -n '/^# / { s/# //; p; q; }' "$src" | tr '"' "'")
    if [[ -z "$title" ]]; then
        title="$SUBTITLE"
    fi

    if [[ ! -d "$dest_dir" ]]; then
        mkdir -p "$dest_dir"
    fi

    if [[ "$format" == html ]]; then
        cat "$HTML_HEADER" > "$dest.tmp"
        html::fromgmi < "$src" >> "$dest.tmp"
        cat "$HTML_FOOTER" >> "$dest.tmp"

        # For HTML, we can override the style sheet per directory.
        local stylesheet="$(basename "$HTML_CSS_STYLE")"
        local stylesheet_override="${stylesheet/.css/-override.css}"
        if [[ "$CONTENT_BASE_DIR/html" != "$(dirname "$dest")" ]]; then
            stylesheet="../$stylesheet"
        fi
        $SED -i "s|%%TITLE%%|$title|g;
                 s|%%DOMAIN%%|$DOMAIN|g;
                 s|%%GEMTEXTER%%|$GEMTEXTER|g;
                 s|%%STYLESHEET%%|$stylesheet|g;
                 s|%%STYLESHEET_OVERRIDE%%|$stylesheet_override|g;" "$dest.tmp"

    elif [[ "$format" == md ]]; then
        md::fromgmi < "$src" >> "$dest.tmp"

    else
        log ERROR "Unknown output format '$format'"
        exit 2
    fi

    mv "$dest.tmp" "$dest"
}

# Generate a given output format from a Gemtext file.
generate::fromgmi () {
    local -i num_gmi_files=0
    local -i num_doc_files=0

    log INFO "Generating $* from Gemtext"

    # Add atom feed for HTML
    generate::convert_gmi_atom_to_html_atom 'html'

    # Add content
    while read -r src; do
        if test -n "$CONTENT_FILTER" && ! $GREP -q "$CONTENT_FILTER" <<< "$src"; then
            continue
        fi

        num_gmi_files=$(( num_gmi_files + 1 ))
        log INFO "Generating output formats from $src"
        for format in "$@"; do
            generate::_to_output_format "$src" "$format" &
        done
    done < <(find "$CONTENT_BASE_DIR/gemtext" -type f -name \*.gmi)

    wait
    log INFO "Converted $num_gmi_files Gemtext files"

    # Add non-.gmi files to html dir.
    log VERBOSE "Adding other docs to $*"

    while read -r src; do
        num_doc_files=$(( num_doc_files + 1 ))
        for format in "$@"; do
            generate::fromgmi_add_docs "$src" "$format" &
        done
    done < <(find "$CONTENT_BASE_DIR/gemtext" -type f | $GREP -E -v '(\.git.*|\.gmi|\.gmi\.tpl|atom.xml|\.tmp)$')
    wait

    log INFO "Added $num_doc_files other documents to each of $*"

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

    # Add extra content
    for format in "$@"; do
        if [[ "$format" == html ]]; then
            log INFO "Adding HTML extras"
            html::add_extras &
        fi
    done
    wait

    for format in "$@"; do
        log INFO "$format can be found in $CONTENT_BASE_DIR/$format now"
    done
    log INFO "You may want to commit all changes to version control!"
}

# Only generate draft posts
generate::draft () {
    if [[ -n "$CONTENT_FILTER" && "$CONTENT_FILTER" != DRAFT- ]]; then
        log ERROR "ERROR, you can't set a content filter manually in draft mode"
        exit 2
    fi
    CONTENT_FILTER=DRAFT-
    generate::fromgmi "$@"

    log INFO 'For HTML preview, open in your browser:'
    find "$CONTENT_BASE_DIR/html" -name DRAFT-\*.html
}
