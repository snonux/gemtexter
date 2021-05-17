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

    if grep -E -q "$IMAGE_PATTERN" <<< "$link"; then
        if [[ "$what" == md ]]; then
            md::make_img "$link" "$descr"
        else
            html::make_img "$link" "$(html::special "$descr")"
        fi
        return
    fi

    if [[ "$what" == md ]]; then
        md::make_link "$link" "$descr"
    else
        html::make_link "$link" "$(html::special "$descr")"
    fi
}

generate::fromgmi_ () {
    local -r src="$1"; shift
    local -r format="$1"; shift
    local dest=${src/gemtext/$format}
    dest=${dest/.gmi/.$format}
    local dest_dir=$(dirname "$dest")

    test ! -d "$dest_dir" && mkdir -p "$dest_dir"
    if [[ "$format" == html ]]; then
        cat header.html.part > "$dest.tmp"
        html::fromgmi < "$src" >> "$dest.tmp"
        cat footer.html.part >> "$dest.tmp"
    elif [[ "$format" == md ]]; then
        md::fromgmi < "$src" >> "$dest.tmp"
    fi

    mv "$dest.tmp" "$dest"
    test "$ADD_GIT" == yes && git add "$dest"
}

generate::fromgmi_add_docs () {
    local -r src="$1"; shift
    local -r format="$1"; shift
    local -r dest=${src/gemtext/$format}
    local -r dest_dir=$(dirname "$dest")

    test ! -d "$dest_dir" && mkdir -p "$dest_dir"
    cp "$src" "$dest"
    test "$ADD_GIT" == yes && git add "$dest"
}

generate::convert_gmi_atom_to_html_atom () {
    local -r format="$1"; shift
    test "$format" != html && return

    log INFO 'Converting Gemtext Atom feed to HTML Atom feed'

    $SED 's|.gmi|.html|g; s|gemini://|https://|g' \
        < $CONTENT_DIR/gemtext/gemfeed/atom.xml \
        > $CONTENT_DIR/html/gemfeed/atom.xml

    test "$ADD_GIT" == yes && git add "$CONTENT_DIR/html/gemfeed/atom.xml"
}

generate::fromgmi_cleanup () {
    local -r src="$1"; shift
    local -r format="$1"; shift
    local dest=${src/.$format/.gmi}
    dest=${dest/$format/gemtext}

    test ! -f "$dest" && test "$ADD_GIT" == yes && git rm "$src"
}

generate::fromgmi () {
    local -i num_gmi_files=0
    local -i num_doc_files=0

    log INFO "Generating $* from Gemtext"

    while read -r src; do
        (( num_gmi_files++ ))
        for format in "$@"; do
            generate::fromgmi_ "$src" "$format"
        done
    done < <(find "$CONTENT_DIR/gemtext" -type f -name \*.gmi)

    log INFO "Converted $num_gmi_files Gemtext files"

    # Add non-.gmi files to html dir.
    log VERBOSE "Adding other docs to $*"

    while read -r src; do
        (( num_doc_files++ ))
        for format in "$@"; do
            generate::fromgmi_add_docs "$src" "$format"
        done
    done < <(find "$CONTENT_DIR/gemtext" -type f | grep -E -v '(.gmi|atom.xml|.tmp)$')

    log INFO "Added $num_doc_files other documents to each of $*"

    # Add atom feed for HTML
    for format in "$@"; do
        generate::convert_gmi_atom_to_html_atom "$format"
    done

    # Remove obsolete files from ./html/
    for format in "$@"; do
        find "$CONTENT_DIR/$format" -type f | while read -r src; do
            generate::fromgmi_cleanup "$src" "$format"
        done
    done

    for format in "$@"; do
        log INFO "$format can be found in $CONTENT_DIR/$format now"
    done
}
