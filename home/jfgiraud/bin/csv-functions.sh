#!/bin/bash

# DESCRIPTION
# Utilities to parse and get values in a csv file using column names.
# See function : csvexample 
#
# AUTHOR
# Written by Jean-François Giraud.
#
# COPYRIGHT
# Copyright © 2013 Jean-François Giraud. License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
# This is free software: you are free to change and redistribute it. There is NO WARRANTY, to the extent permitted by law.

csvindexes() {
    local hashname=$1
    local file=$2
    eval "$hashname=( )"
    eval $(head -n 1 $file | tr ';' '\n' | awk -v h="$hashname" '{print h"["$1"]="NR}')
}

csvfilter() {
    local hashname=$1
    shift
    [ -z "$1" ] && cat && return
    local filter=$1
    local key=$(echo $filter | cut -d '=' -f 1)
    local value=$(echo $filter | cut -d '=' -f 2)
    eval $(printf 'keyindex=${%s[%s]}' $hashname $key)
    shift
    awk -F ';' -v k=$keyindex -v v=$value '$k==v {print}' | csvfilter $hashname $*
}

csvextract() {
    local hashname=$1
    local tuple=$2
    shift 2
    until [ -z "$1" ]; do
	local filter=$1
	local key=$(echo $filter | cut -d '=' -f 1)
	local value=$(echo $filter | cut -d '=' -f 2)
	eval $(printf 'keyindex=${%s[%s]}' $hashname $value)
	shift
	#echo $filter $key $value
	echo $tuple | awk -F ';' -v k=$keyindex -v v=$key '{print v"="$k}'
    done
}

csvvalues() {
    tail -n +2 $1
}

csvexample() {
    (cat <<-EOF
lastname;firstname;birth;number_of_child
doe;john;1975;2
doe;foo;1990;1
doe;jane;1985;2
EOF
) > example.csv
    declare -A persons
    csvindexes persons example.csv
    for tuple in $(csvvalues example.csv | csvfilter persons "lastname=doe" "birth=1985" "number_of_child=2")
    do
	eval $(csvextract persons $tuple "vara=lastname" "varb=firstname" "varc=birth" "vard=number_of_child")
	echo "vara=$vara"
	echo "varb=$varb"
	echo "varc=$varc"
	echo "vard=$vard"
    done
    rm -f example.csv
}

#csvexample
