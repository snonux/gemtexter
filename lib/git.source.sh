git::_content_dirs_in_git () {
    find "$CONTENT_BASE_DIR" -maxdepth 1 -mindepth 1 -type d |
    while read -r content_dir; do
        if [ -d "$content_dir/.git" ]; then
            echo "$content_dir"
        fi
    done
}

git::add_all () {
    local message="$1"; shift
    if [ -z "$message" ]; then
        message='Update content'
    fi

    git::_content_dirs_in_git | while read -r content_dir; do
        log INFO "Adding content from $content_dir to git"
        git::_add_all "$message" "$content_dir"
    done
}

git::_add_all () {
    local -r message="$1"; shift
    local -r content_dir="$1"; shift
    local -r pwd="$(pwd)"
    cd "$content_dir" || log PANIC "Unable to chdir to $content_dir"

    find . -type f -not -path '*/\.git*' | while read -r file; do
        git add "$file"
    done

    local -r format="$(basename "$content_dir")"
    if ! git commit -a -m "$message for $format"; then
        log INFO 'Nothing new to be added'
    fi

    cd "$pwd"
}

git::sync_all () {
    git::_content_dirs_in_git | while read -r content_dir; do
        log INFO "Synchronizing content from $content_dir with remote git"
        git::_sync_all "$content_dir"
    done
}

git::_sync_all () {
    local -r content_dir="$1"; shift
    cd "$content_dir" || log PANIC "Unable to chdir to $content_dir"

    git pull
    git push
    git status

    cd -
}

