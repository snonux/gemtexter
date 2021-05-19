#!/usr/bin/env bash
#
# The buetow.org.sh static site generator
# by Paul Buetow 2021

declare -r ARG="$1"; shift
declare DATE=date
declare SED=sed
declare GREP=grep
which gdate &>/dev/null && DATE=gdate
which gsed &>/dev/null && SED=gsed
which ggrep &>/dev/null && GREP=ggrep
readonly DATE
readonly SED
readonly GREP

source buetow.org.conf
source ./packages/assert.source.sh
source ./packages/atomfeed.source.sh
source ./packages/gemfeed.source.sh
source ./packages/generate.source.sh
source ./packages/html.source.sh
source ./packages/log.source.sh
source ./packages/md.source.sh

help () {
    cat <<HELPHERE
$0's possible arguments:
    --feed
    --publish
    --test
    --help
HELPHERE
}

main () {
    local -r arg="$1"; shift

    case $ARG in
        --test)
            html::test
            md::test
            ;;
        --feed)
            gemfeed::generate
            atomfeed::generate
            ;;
        --generate)
            html::test
            md::test
            gemfeed::generate
            atomfeed::generate
            generate::fromgmi html md
            ;;
        --help|*)
            help
            ;;
    esac

    return 0
}

main $ARG
exit $?
