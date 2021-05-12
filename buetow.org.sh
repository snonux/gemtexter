#!/usr/bin/env bash
#
# The buetow.org.sh static site generator
# by Paul Buetow 2021

declare -r ARG=$1; shift
declare DATE=date
declare SED=sed
which gdate &>/dev/null && DATE=gdate
which gsed &>/dev/null && SED=gsed

source buetow.org.conf
source ./modules/assert.source.sh
source ./modules/atomfeed.source.sh
source ./modules/gemfeed.source.sh
source ./modules/generate.source.sh
source ./modules/html.source.sh
source ./modules/log.source.sh
source ./modules/md.source.sh

help () {
    cat <<HELPHERE
$0's possible arguments:
    --feed
    --publish
    --test
    --help
HELPHERE
}

case $ARG in
    --test)
        html::test
        md::test
        ;;
    --feeds)
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

exit 0
