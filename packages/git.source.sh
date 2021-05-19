# Add a static content file to git
git::add () {
    local -r content_dir="$CONTENT_BASE_DIR/$1"; shift
    local file="$1"; shift
    file=${file/$content_dir/}

    cd $content_dir
    echo git add $file
    cd -
}

# Remove a static content file from git
git::rm () {
    local -r content_dir="$CONTENT_BASE_DIR/$1"; shift
    local file="$1"; shift
    file=${file/$content_dir/}

    cd $content_dir
    echo git rm $file
    cd -
}

# Commit all changes
git::commit () {
    local -r content_dir="$CONTENT_BASE_DIR/$1"; shift
    local -r message="$1"; shift

    cd $content_dir
    echo git commit -a -m "$message"
    cd -
}
