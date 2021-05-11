#!/usr/bin/env bash

declare -r ARG=$1; shift
declare DATE=date
declare SED=sed
which gdate &>/dev/null && DATE=gdate
which gsed &>/dev/null && SED=gsed

source buetow.org.conf
source ./lib/assert.source.sh
source ./lib/atomfeed.source.sh
source ./lib/gemfeed.source.sh
source ./lib/generate.source.sh
source ./lib/html.source.sh
source ./lib/md.source.sh

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
