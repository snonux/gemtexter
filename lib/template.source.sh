template::generate () {
    log INFO 'Generating files from templates'
    local -i num_tpl_files=0
    declare -A _TPL_DIR_NEWEST_MTIME

    while read -r tpl_path; do
        if test -n "$CONTENT_FILTER" && ! $GREP -q "$CONTENT_FILTER" <<< "$tpl_path"; then
            continue
        fi
        num_tpl_files=$(( num_tpl_files + 1 ))
        template::_generate_file "$tpl_path"
    done < <(find "$CONTENT_BASE_DIR/gemtext" -type f -name \*.gmi.tpl)

    wait
    log INFO "Converted $num_tpl_files template files"
}

template::draft () {
    CONTENT_FILTER=DRAFT-
    template::generate
}

# Compute the newest mtime among .gmi.tpl files and non-template .gmi files
# in a given directory. Result is cached in _TPL_DIR_NEWEST_MTIME associative array.
template::_dir_newest_mtime () {
    local -r dir="$1"; shift

    if [[ -n "${_TPL_DIR_NEWEST_MTIME[$dir]+x}" ]]; then
        echo "${_TPL_DIR_NEWEST_MTIME[$dir]}"
        return
    fi

    # Find newest mtime among .gmi.tpl files and non-template, non-index .gmi files
    local newest=0
    local mtime
    while read -r mtime _; do
        mtime=${mtime%%.*}
        if (( mtime > newest )); then
            newest=$mtime
        fi
    done < <(find "$dir" -maxdepth 1 \( -name '*.gmi.tpl' -o -name '*.gmi' \) -type f \
             ! -name 'index.gmi' -printf '%T@ %p\n')

    _TPL_DIR_NEWEST_MTIME[$dir]="$newest"
    echo "$newest"
}

template::_generate_file () {
    local -r tpl_path="$1"; shift
    local -r tpl_dir="$(dirname "$tpl_path")"
    local -r tpl="$(basename "$tpl_path")"
    local -r dest="${tpl/.tpl/}"

    # Skip if output is newer than the template and all relevant siblings
    if [[ "$FORCE_REBUILD" != yes ]] && [[ -f "$tpl_dir/$dest" ]]; then
        local -r dest_mtime=$(stat -c '%Y' "$tpl_dir/$dest")
        local -r dir_newest=$(template::_dir_newest_mtime "$tpl_dir")
        if (( dest_mtime >= dir_newest )); then
            log VERBOSE "Skipping unchanged template $tpl_path"
            return
        fi
    fi

    cd "$tpl_dir" || log PANIC "Unable to chdir to $tpl_dir"
    log INFO "Generating $tpl_path -> $dest"

    # Environment variables can be used from .gmi.tpl files
    export CURRENT_TPL="$tpl_path"
    export CURRENT_GMI="$dest"

    template::_generate < "$tpl" > "$dest.tmp"

    # Only overwrite if content actually changed, preserving mtime for caches
    generate::safe_overwrite "$dest.tmp" "$dest"
    cd - >/dev/null
}

template::_generate () {
    local is_block=no
    local block=''

    while IFS='' read -r line; do
        if [ "$is_block" = yes ]; then
            if [ "$line" = '>>>' ]; then
                # Eval template block with error context for debuggability
                if ! eval "$block"; then
                    log ERROR "Template block eval failed in ${CURRENT_TPL:-unknown}"
                    log ERROR "Block content: $block"
                fi
                is_block=no
                block=''
            else
                block="$block
$line"
            fi
            continue
        fi
        case "$line" in
            '<< '*)
                template::_line "$line"
                ;;
            '<<<'*)
                is_block=yes
                ;;
            *)
                echo "$line"
                ;;
        esac
    done | $SED -E '
        /^```/,/^```/! {
            s/^\[\[\[/<<</;
            s/^\]\]\]/>>>/;
            s/^\[\[/<</;
            s/^\]/>/;
        }
    '
}

# Evaluate a single template line (e.g. '<< echo foo')
template::_line () {
    if ! eval "${1/<< /}"; then
        log ERROR "Template line eval failed in ${CURRENT_TPL:-unknown}: $1"
    fi
}

# Sugesting adding a ToC when there are many sections
template::suggester::toc () {
    find "$CONTENT_BASE_DIR/gemtext" -name \*.gmi | while read -r gmi_file; do
        if test -f "$gmi_file.tpl" && $GREP -q '<< template::inline::toc' "$gmi_file.tpl"; then
            continue # Has alread a ToC
        fi    
        local -i num_sections="$($SED -E -n '/^```/,/^```/! { /^#+ /p; }' "$gmi_file" | wc -l)"
        if [ $num_sections -ge 7 ]; then
            echo "$gmi_file with $num_sections sections and no ToC - consider adding template::inline::toc!"
        fi
    done
}


# Can be used from a .gmi.tpl template for generating an index for a given topic.
template::inline::_index () {
    local topic=''
    for topic in "$@"; do 
        while read -r gmi_file; do
            local date=$(cut -d- -f1,2,3 <<< "$gmi_file")
            local title=$($SED -n "/^# / { s/# //; p; q; }" "$gmi_file")

            local current=''
            if [ "$gmi_file" = "$CURRENT_GMI" ]; then
                current=" (You are currently reading this)"
            fi

            echo "=> ./$gmi_file $date $title$current"
        done < <(ls | $GREP -i "$topic.*\\.gmi\$" | $GREP -v DRAFT)
    done
}

# Can be used from a .gmi.tpl template for generating an index for a given topic.
template::inline::index () {
    template::inline::_index "$@" | sort | uniq
}

# Same as index, but reverse order
template::inline::rindex () {
    template::inline::_index "$@" | sort -r | uniq
}

# TODO: Write unit test.
# To generate a table of contents
template::inline::toc () {
    echo '## Table of Contents'
    echo ''
    < "$(basename "$CURRENT_TPL")" $SED -E -n '
        /^```/,/^```/! {
            /^#+ / {
                s/^###/* ⇢ ⇢ ⇢/
                s/^##/* ⇢ ⇢/
                s/^#/* ⇢/
                p
            }
        }
    '
}

template::test () {
    assert::equals "$(template::_line '<< echo -n foo')" 'foo'
    assert::equals "$(template::_line '<< echo foo')" 'foo'
    assert::equals "$(template::_line '<< $DATE --date @0 +%Y%m%d')" '19700101'
    assert::equals "$(template::_line '<< echo "$AUTHOR"')" "$AUTHOR"

    template::_line '<< foo=bar'
    assert::equals "$(template::_line '<< echo $foo')" bar

    local -r template1='# Hello Mister
<<<
    echo -n "Epoch 0 starts at: "
    $DATE --date @0 +%Y%m%d
    echo Just so that you know
>>>'
    local -r expect1='# Hello Mister
Epoch 0 starts at: 19700101
Just so that you know'
    assert::equals "$(template::_generate <<< "$template1")" "$expect1"

    local -r template2='<<<
    for i in {1..10}; do
        echo -n $i
    done
>>>'
    assert::equals "$(template::_generate <<< "$template2")" 12345678910

    local -r template3='<<<
    foo=baz
>>>
<<<bash
    echo $foo
>>>'
    assert::equals "$(template::_generate <<< "$template3")" baz

    local -r template4='<<<
>>>
<<<
>>>
<< :'
    assert::equals "$(template::_generate <<< "$template4")" ''

    local -r template5='[[ echo foo
[[[
    echo bar
]]]'
    local -r expect5='<< echo foo
<<<
    echo bar
>>>'
    assert::equals "$(template::_generate <<< "$template5")" "$expect5"

    assert::equals "$(template::_generate <<< ']')" '>'

#     local -r template6='# Hello world

# << template::inline::toc    

# ## Heading 1

# ### Heading 1b
 
# foo bar baz

# ## Heading 2
 
# ### Heading 2b

# foo bar baz'

#     local -r expect6='<< echo foo
# <<<
#     echo bar
# >>>'
#     assert::equals "$(template::_generate <<< "$template6")" "$expect6"

#     assert::equals "$(template::_generate <<< ']')" '>'
}
