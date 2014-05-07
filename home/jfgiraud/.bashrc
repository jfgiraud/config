shopt -s autocd
shopt -s cdspell

export EDITOR=vim

if [[ ! "$PATH" =~ (^|:)"$HOME/bin"(:|$) ]]; then
    export PATH="$PATH:$HOME/bin"
fi

function sib() {
    ## sib <substr> search sibling directories 
    ##   prompt for choice (when two or more directories are found) 
    ##   change to directory after prompt
    ## sib -- [ first | last | previous | next ]
    local substr=$1
    if [ "X$substr" == "X--" ]; then
	shift
	substr=$1
	if [ "$substr" == "first" ]; then
	    local dir=$(find .. -maxdepth 1 -type d | grep -vE '^..$' | sed -e 's:../::' | sort | head -n 1)
	    cd ../$dir
	    return 0
	elif [ "$substr" == "last" ]; then
	    local dir=$(find .. -maxdepth 1 -type d | grep -vE '^..$' | sed -e 's:../::' | sort | tail -n 1)
	    cd ../$dir
	    return 0
	elif [ "$substr" == "next" ]; then
	    local curdir=$(pwd)
	    curdir=${curdir##*/}
	    local dir=$(find .. -maxdepth 1 -type d | grep -vE '^..$' | sed -e 's:../::' | sort | grep -E -A 1 "^${curdir}$" | tail -n 1)
	    if [ "$curdir" == "$dir" ]; then
		echo "No next sibling directory!"
		return 1
	    else
		cd ../$dir
		return 0
	    fi
	elif [ "$substr" == "previous" ]; then
	    local curdir=$(pwd)
	    curdir=${curdir##*/}
	    local dir=$(find .. -maxdepth 1 -type d | grep -vE '^..$' | sed -e 's:../::' | sort | grep -E -B 1 "^${curdir}$" | head -n 1)
	    if [ "$curdir" == "$dir" ]; then
		echo "No previous sibling directory!"
		return 1
	    else
		cd ../$dir
		return 0
	    fi
	else
	    echo "Not understood!"
	    return 1
	fi
    fi
    local curdir=$(pwd)
    local choices=$(find .. -maxdepth 1 -type d -name "*${substr}*" | grep -vE '^..$' | sed -e 's:../::' | grep -vE "^${curdir##*/}$" | sort)
    if [ -z "$choices" ]; then
	echo "Sibling directory not found!"
	return 1
    fi
    local count=$(echo "$choices" | wc -l)
    if [[ $count -eq 1 ]]; then
	cd ../$choices
	return 0
    fi
    select dir in $choices; do
	if [ -n "$dir" ]; then
	    cd ../$dir
	    return 0
	fi
	break
    done
}

alias sibn='sib -- next'
alias sibp='sib -- previous'
alias sibf='sib -- first'
alias sibl='sib -- last'

function chd() {
    ## chd <substr> search children directories 
    ##   prompt for choice (when two or more directories are found) 
    ##   change to directory after prompt 
    local substr=$1
    local curdir=$(pwd)
    local choices=$(find . -maxdepth 1 -type d -name "*${substr}*" | grep -vE '^.$' | sed -e 's:./::' | sort)
    if [ -z "$choices" ]; then
	echo "No child directory not found!"
	return
    fi
    local count=$(echo "$choices" | wc -l)
    if [[ $count -eq 1 ]]; then
	cd ./$choices
	return 
    fi
    select dir in $choices; do
	if [ -n "$dir" ]; then
	    cd ./$dir
	fi
	break
    done
}


function svn-cmp () {
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

function svn-clean () {
    local choices=$(LC_CTYPE=en_US.UTF-8 svn st | awk '/^?/ { print $2 }')
    if [ -z "$choices" ]; then
	return
    fi
    select choice in '(all files)' $choices; do
	break
    done
    if [ -n "$choice" ]; then
	if [ "$choice" == '(all files)' ]; then
	    rm -f $(LC_CTYPE=en_US.UTF-8 svn st | awk '/^?/ { print $2 }')
	else
	    rm -f "$choice"
	fi
    fi
}

function _apply_on_str() {
    local cmd="$1"
    shift
    if [[ $# -eq 0 || "$1" == "-" ]]; then
	cat - | eval $cmd
    else
	while [ $# -gt 0 ]; do
	    local text="$1"
	    echo $text | eval $cmd
	    shift
	done
    fi
}

function unaccent() {
    _apply_on_str "iconv -f utf8 -t ascii//TRANSLIT//IGNORE" "${@}"
}

function unpunct() {
    _apply_on_str "tr -d '[[:punct:]]'" "${@}"
}

function uncntrl() {
    _apply_on_str "tr -d '[[:cntrl:]]'" "${@}"
}

function unspace() {
    _apply_on_str "tr -d '[[:space:]]'" "${@}"
}

function unspace1() {
    _apply_on_str "tr -s '[[:space:]]' ' '" "${@}"
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

function mktouch() {
    local path="$1"
    dn=${path%/*}
    fn=${path%/*}
    if [ ! -d "$dn" ]; then
	mkdir -p "$dn"
    fi
    touch "$path"
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

