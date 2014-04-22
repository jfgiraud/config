#!/bin/bash

function get_credentials () {
    local account="$1"
    awk $"BEGIN { RS=\"\n\n\" } /(^|\n)account ${account}(\n|$)/ { print }" ~/.netrc | sed -e 's/ /="/' -e 's/$/"/'
}

get_credentials $*
