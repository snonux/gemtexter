# Git can not run concurrently
git::_lock () {
    local -r lock="${CONTENT_BASE_DIR}/git.lock"

    while test -d $lock; do
        sleep 0.1
    done
    while ! mkdir $lock 2>/dev/null; do
        sleep 0.1
    done
}

git::_unlock () {
    local -r lock="${CONTENT_BASE_DIR}/git.lock"
    rmdir $lock
    # log DEBUG "Removed $lock"
}

git::cleanup () {
    local -r lock="${CONTENT_BASE_DIR}/git.lock"
    if [ -d "$lock" ]; then
        git::_unlock
    fi
}

# Add a static content file to git
git::add () {
    if [[ "$USE_GIT" != yes ]]; then
        return
    fi

    local -r content_dir="$CONTENT_BASE_DIR/$1"; shift
    local file="$1"; shift
    file=${file/$content_dir/.\/}

    git::_lock
    cd "$content_dir" &>/dev/null
    git add "$file"
    cd - &>/dev/null
    git::_unlock
}

# Remove a static content file from git
git::rm () {
    if [[ "$USE_GIT" != yes ]]; then
        return
    fi

    local -r content_dir="$CONTENT_BASE_DIR/$1"; shift
    local file="$1"; shift
    file=${file/$content_dir/.\/}

    git::_lock
    cd "$content_dir" &>/dev/null
    git rm "$file"
    cd - &>/dev/null
    git::_unlock
}

# Commit all changes
git::commit () {
    if [[ "$USE_GIT" != yes ]]; then
        return
    fi

    local -r content_dir="$CONTENT_BASE_DIR/$1"; shift
    local -r message="$1"; shift

    git::_lock
    cd "$content_dir" &>/dev/null
    set +e
    git commit -a -m "$message"
    if [[ "$GIT_PUSH" == yes ]]; then
        log INFO "Invoking git pull/push in $content_dir"
        git pull
        git push
    fi
    set -e
    cd - &>/dev/null
    git::_unlock
}
