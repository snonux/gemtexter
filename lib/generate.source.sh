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

# Markdown internal href format, we use it also for HTML
generate::internal_link_id () {
    local -r text="$1"; shift
    # Replace uppercase with lowercase
    # Replace ' and space with dashes
    # Remove all other characters but alnum
    tr '[:upper:]' '[:lower:]' <<< "$text" | tr "' " '-' | tr -cd 'A-Za-z0-9-'
}

# Atomically replace a file only if content actually changed, preserving mtime
# for downstream skip logic. Removes the temp file if unchanged.
generate::safe_overwrite () {
    local -r tmp_file="$1"; shift
    local -r dest_file="$1"; shift

    if [[ -f "$dest_file" ]] && diff -q "$tmp_file" "$dest_file" >/dev/null 2>&1; then
        rm "$tmp_file"
    else
        mv "$tmp_file" "$dest_file"
    fi
}

# Add other docs (e.g. images, videos) from Gemtext to output format.
# Skips copying if the output file already exists and is newer than the source.
generate::fromgmi_add_docs () {
    local -r src="$1"; shift
    local -r format="$1"; shift
    local -r dest=${src/gemtext/$format}
    local -r dest_dir=$(dirname "$dest")

    # Skip if output already exists and is newer than source
    if [[ -f "$dest" ]] && [[ "$dest" -nt "$src" ]]; then
        return
    fi

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
    local -r current_page="$1"; shift
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
                 s|%%MARKDOWN_BASE_URI%%|$MARKDOWN_BASE_URI|g;
                 s|%%CURRENT_PAGE%%|$current_page|g;
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

# Check if any global dependency (header, footer, CSS, config) has changed
# since the last generation. Sets _force_rebuild=yes if so.
generate::_check_global_deps () {
    local -r sentinel="$CONTENT_BASE_DIR/.gemtexter.lastgen"

    if [[ "$FORCE_REBUILD" == yes ]]; then
        _force_rebuild=yes
        return
    fi

    if [[ ! -f "$sentinel" ]]; then
        _force_rebuild=yes
        return
    fi

    local dep
    for dep in "$HTML_HEADER" "$HTML_FOOTER" "$HTML_CSS_STYLE" ./gemtexter.conf; do
        if [[ -f "$dep" ]] && [[ "$dep" -nt "$sentinel" ]]; then
            log INFO "Global dependency $dep changed, forcing full rebuild"
            _force_rebuild=yes
            return
        fi
    done

    _force_rebuild=no
}

# Check if a source .gmi file is fresh (all outputs newer than source).
# Returns 0 (true) if all outputs exist and are newer, meaning we can skip.
generate::_is_fresh () {
    local -r src="$1"; shift

    if [[ "$_force_rebuild" == yes ]]; then
        return 1
    fi

    local format dest
    for format in "$@"; do
        dest=${src/gemtext/$format}
        dest=${dest/.gmi/.$format}
        if [[ ! -f "$dest" ]] || [[ "$src" -nt "$dest" ]]; then
            return 1
        fi
    done

    return 0
}

# Generate a given output format from a Gemtext file.
generate::fromgmi () {
    local -i num_gmi_files=0
    local -i num_skipped_files=0
    local -i num_doc_files=0
    local current_page
    local _force_rebuild=no

    # Cap concurrent jobs to the number of CPU cores
    local -r max_jobs=$(( $(nproc 2>/dev/null || echo 4) ))

    log INFO "Generating $* from Gemtext"

    # Check if global deps changed (header, footer, CSS, config)
    generate::_check_global_deps

    # Add atom feed for HTML
    generate::convert_gmi_atom_to_html_atom 'html'

    # Add content
    while read -r src; do
        if test -n "$CONTENT_FILTER" && ! $GREP -q "$CONTENT_FILTER" <<< "$src"; then
            continue
        fi

        # Skip files where all outputs are newer than the source
        if generate::_is_fresh "$src" "$@"; then
            log VERBOSE "Skipping unchanged $src"
            num_skipped_files=$(( num_skipped_files + 1 ))
            continue
        fi

        current_page=$($SED "s|$CONTENT_BASE_DIR/gemtext||;"'s/.gmi$//;' <<< "$src")
        num_gmi_files=$(( num_gmi_files + 1 ))
        log INFO "Generating output formats from $src"
        for format in "$@"; do
            # Throttle: wait for a job slot before spawning
            while (( $(jobs -rp | wc -l) >= max_jobs )); do
                wait -n
            done
            generate::_to_output_format "$src" "$current_page" "$format" &
        done
    done < <(find "$CONTENT_BASE_DIR/gemtext" -type f -name \*.gmi)

    wait
    log INFO "Converted $num_gmi_files Gemtext files (skipped $num_skipped_files unchanged)"

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
        $GREP -E -v '(\.git.*|_config.yml|CNAME|.domains|robots.txt|static|\.tmp)$'|
        while read -r src; do
            generate::fromgmi_cleanup_docs "$src" "$format" 
        done &
    done
    wait

    # Add extra content
    for format in "$@"; do
        if [[ "$format" == html ]]; then
            log INFO "Adding HTML theme files "
            html::theme &
        fi
    done
    wait

    for format in "$@"; do
        log INFO "$format can be found in $CONTENT_BASE_DIR/$format now"
    done

    # Update sentinel file so next run can detect global dep changes
    touch "$CONTENT_BASE_DIR/.gemtexter.lastgen"

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

generate::test () {
    local text="I can't believe it!"
    assert::equals "$(generate::internal_link_id "$text")" 'i-can-t-believe-it'

    # Test generate::safe_overwrite: dest does not exist, tmp should be moved
    local tmp_dir=$(mktemp -d)
    echo 'new content' > "$tmp_dir/file.tmp"
    generate::safe_overwrite "$tmp_dir/file.tmp" "$tmp_dir/file"
    assert::equals "$(cat "$tmp_dir/file")" 'new content'
    assert::equals "$(test -f "$tmp_dir/file.tmp" && echo exists || echo gone)" 'gone'

    # Test generate::safe_overwrite: dest exists and is identical, mtime preserved
    local before_mtime=$(stat -c '%Y' "$tmp_dir/file")
    sleep 1
    echo 'new content' > "$tmp_dir/file.tmp"
    generate::safe_overwrite "$tmp_dir/file.tmp" "$tmp_dir/file"
    local after_mtime=$(stat -c '%Y' "$tmp_dir/file")
    assert::equals "$before_mtime" "$after_mtime"
    assert::equals "$(test -f "$tmp_dir/file.tmp" && echo exists || echo gone)" 'gone'

    # Test generate::safe_overwrite: dest exists but differs, content replaced
    echo 'different content' > "$tmp_dir/file.tmp"
    generate::safe_overwrite "$tmp_dir/file.tmp" "$tmp_dir/file"
    assert::equals "$(cat "$tmp_dir/file")" 'different content'
    assert::equals "$(test -f "$tmp_dir/file.tmp" && echo exists || echo gone)" 'gone'

    rm -rf "$tmp_dir"
}
