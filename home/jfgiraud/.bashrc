shopt -s autocd
shopt -s cdspell

export EDITOR=vim

if [[ ! "$PATH" =~ (^|:)"$HOME/bin"(:|$) ]]; then
    export PATH="$PATH:$HOME/bin"
fi

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

alias ll='./bin/sql-connect -ll'
alias g='./bin/sql-connect -g'
alias lv='./bin/sql-connect -v'
alias ff='find . -type f | grep -v svn'
alias cleandir=$'find . \( -name \'*~\' -o -name \'#*#\' \) -exec rm -v {} \;'
