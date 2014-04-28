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
    local curdir=$(pwd)
    local choices=$(find .. -maxdepth 1 -type d -name "*${substr}*" | grep -vE '^..$' | sed -e 's:../::' | grep -vE "^${curdir##*/}$" | sort)
    if [ -z "$choices" ]; then
	echo "Sibling directory not found!"
	return
    fi
    local count=$(echo "$choices" | wc -l)
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

function svncmp () {
    if [ ! -x "$HOME/bin/cdiff" ]; then
	echo "Please install 'cdiff' program in $HOME/bin/ directory (https://github.com/ymattw/cdiff)"
	return 1
    fi
    local file="$1"
    local rev="$2"
    local choices=$(LC_ALL=C svn log "$file" | awk '/^r[[:digit:]]+[[:space:]]+/ { gsub("r", "", $1); print $1 }' | sort -r | tail -n +2)
    local revision=""
    if [[ "$rev" =~ ^-[0-9]+$ || "$rev" == "-" ]]; then
	rev=${rev#-}
	if [ -z "$rev" ]; then
	    rev="1"
	fi
	revision=$(echo $choices | cut -d " " -f $rev)
    else
	select choice in $choices; do
	    revision=$choice
	    break
	done
    fi
    if [ -n "$revision" ]; then
	$HOME/bin/cdiff -s --width=$(( $(tput cols) / 2 )) -r"$revision" "$file"
    fi
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

function swap() {
    local f1="$1"
    local f2="$2"
    if [ -e "$f1" -a -e "$f2" ]; then
        local ftmp=$(mktemp)
        mv "$f1" $ftmp
        mv "$f2" "$f1"
        mv $ftmp "$f2"
    else
        echo "At least one given path does not exist!"
        return 1
    fi
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

