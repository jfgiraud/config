#!/bin/bash

function select_choice () {
    local account="$1"
    awk $"BEGIN { RS=\"\n\n\" } /(^|\n)account ${account}(\n|$)/ { print }" ~/.netrc | sed -e 's/ /="/' -e 's/$/"/'
}

function get_credentials () {
    local patterns="account $*"
    local choices=()
    while IFS=$'\n' read line || [[ $line ]]; 
    do
	local matches=1
	for pattern in $patterns; do
	    if [[ ! "$line" =~ $pattern ]]; then
		matches=0
		break
	    fi
	done
	if [ $matches -eq 1 ]; then
	    choices+=(${line#account})
	fi
    done < ~/.netrc

    if [ ${#choices[@]} -eq 1 ]; then
	select_choice "${choices[0]}"
	return
    fi

    select choice in ${choices[@]};
    do
	select_choice "$choice"
	break
    done
	
}

get_credentials $*
