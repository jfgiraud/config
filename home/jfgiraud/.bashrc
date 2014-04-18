shopt -s autocd
shopt -s cdspell

export EDITOR=vim

if [[ ! "$PATH" =~ (^|:)"$HOME/bin"(:|$) ]]; then
    export PATH="$PATH:$HOME/bin"
fi

function sib() {
    ## sib <substr> search sibling directories 
    ##   prompt for choic e(when two or more directories are found) 
    ##   change to directory after prompt 
    local substr=$1
    choices=$(find .. -maxdepth 1 -type d -name "*${substr}*" | grep -vE '^..$' | sed -e 's:../::' | sort)
    count=$(echo "$choices" | wc -l)
    if [[ $count -eq 1 ]]; then
	cd ../$choices
	return 
    fi
    select dir in $choices; do
	if [ -n "$dir" ]; then
	    cd ../$dir
	fi
	break
    done
}

function ..() {
    ## .. <number> apply cd .. <number> times
    ## .. /<string> apply cd .. until string is found in current directory name
    ## OLDPWD is modified, so cd - returns to the directory before .. call
    local level=$1
    local _OLDPWD=$(pwd)
    if [[ ! "$level" =~ / ]]; then
	if [ -z $level ]; then
	    cd ..
	    return
	fi
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
    OLDPWD=$_OLDPWD
}

function printx() {
    printf "\\\\u00%.2x" "'$1"
}

function unicode() {
    for c in à â é è ê ë î ï ô ö ù û ü ÿ ç; do printf "$c \\\\u00%.2x\n" "'$c"; done
}

if [[ -e "$HOME/.bashrc_local" ]]; then
    source "$HOME/.bashrc_local"
fi

