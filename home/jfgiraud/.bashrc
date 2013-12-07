shopt -s autocd
shopt -s cdspell

#export PATH=$PATH:/var/lib/gems/1.8/bin
#export PYTHONPATH=~/Logiciels/lib-egg/simplejson-2.1.3-py2.7.egg:$PYTHONPATH

export JAVA_HOME=/usr/lib/jvm/jdk1.7.0_25/
export M2_HOME=/opt/maven/
export EDITOR=vim
export PRIORITY=$JAVA_HOME/bin/

export PATH=$PRIORITY:/opt/ruby1.8/bin/:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin:/usr/bin/vendor_perl:/usr/bin/core_perl

function ..() {
    ## .. <nombre> remonte de <nombre> repertoires
    ## .. /<chaine> remonte jusqu'a ce qu'un repertoire contient <chaine> dans son nom
    local level=$1
    if [[ ! "$level" =~ / ]]; then
	while [ $level -gt 0 ]; do
	    cd .. || break
	    level=$(($level-1))
	done
    else
	level=${level:1}
	local curdir=$(pwd)
	IFS='/' read -ra ADDR <<< "$curdir"
	for (( i = ${#ADDR[@]}-1; i>0; i-- )); do
	    if [[ "${ADDR[$i]}" =~ "$level" ]]; then
		break
	    fi
	    cd ..
	done
    fi
}

function printx() {
    printf "\\\\u00%.2x" "'$1"
}

function unicode() {
    for c in à â é è ê ë î ï ô ö ù û ü ÿ ç; do printf "$c \\\\u00%.2x\n" "'$c"; done
}

function swap() { 
    if [[ -e "$1" && -e "$2" ]]      # if files exist
    then
	local TMPFILE=$(tempfile)
	mv "$1" $TMPFILE
	mv "$2" "$1"
	mv $TMPFILE "$2"
    else
	echo "Error: Make sure the files exist."
    fi
}

function genpass() {
    LENGTH=${1:-10}
    if [ "$2" == "0" ]; then
	CHAR="[:alnum:]"
    elif [ "$2" == "1" ]; then
	CHAR="[:graph:]"
    elif [ "${2:0:1}" != "+" ]; then
	echo "Erreur: vous devez spécifier les caractères acceptés"
	echo "Exemple: $ genpass 32 '+[:alnum:]_'"
	echo "2na2lku4FBqM7eNPC_aooahXV0c8GxI7"
	return
    else
	CHAR="${2:1}"
    fi
    cat /dev/urandom | tr -cd "$CHAR" | head -c $LENGTH
    echo
}

alias run='ant webapp-run'
alias ll='./bin/sql-connect -ll'
alias g='./bin/sql-connect -g'
alias lv='./bin/sql-connect -v'
alias ff='find . -type f | grep -v svn'
alias cleandir=$'find . \( -name \'*~\' -o -name \'#*#\' \) -exec rm -v {} \;'
