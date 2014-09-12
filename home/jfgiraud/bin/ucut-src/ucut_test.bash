#!/bin/bash

# bug : ucut2 -d ',' -s -f $'(4,7)@{ { -> d { d "\\"" "" replace } } q sto q eval swap q eval 2 ->list "{0};{1}"  }' ./villes_france.csv |head
#       produit IOError: [Errno 32] Broken pipe
#
# bug : echo "élo" | ./ucut2 -f 1
#       retour chariot en trop


function assertEquals() {
    echo -n ":: $1: "
    if ! diff result.txt expected.txt > /dev/null; then
        echo "KO"
        echo == expects:
	echo
        cat expected.txt
	echo
        echo == but receives:
	echo
        cat result.txt
	echo
        exit 1
    else
        echo "OK"
    fi
    rm -f result.txt given.txt expected.txt
}

echo "élo" | ./ucut -f 1 > result.txt
echo "élo" > expected.txt
assertEquals "fields - No new line"

echo "élo;" | ./ucut -d';' -f 1 > result.txt
echo "élo" > expected.txt
assertEquals "fields - No new line (field #1)"

echo ";élo" | ./ucut -d';' -f 2 > result.txt
echo "élo" > expected.txt
assertEquals "fields - No new line (field #2)"

echo "azertyéqwerty" | ./ucut -d'é' -f 2 > result.txt
echo "qwerty" > expected.txt
assertEquals "fields - Delimiter with accent (single char)"

echo "azertyéôîqwerty" | ./ucut -d'éôî' -f 2 > result.txt
echo "qwerty" > expected.txt
assertEquals "fields - Delimiter with accent (multiple chars)"

function hex() {
    hexdump -ve '1/1 "%.2x"'
    #cat -
}

echo "élo" | ./ucut -c 1 | hex > result.txt
echo "élo" | cut -c 1 | hex > expected.txt
assertEquals "chars - Accents (1)"

echo "élo" | ./ucut -c 1,3 -o ô | hex > result.txt
echo "élo" | cut -c 1,3 --output-delimiter=ô | hex > expected.txt
assertEquals "chars - Accents (1,3) with output-delimiter set to ô"


echo "élo" | ./ucut -c '1:' | hex > result.txt
echo "élo" | cut -c '1-' | hex > expected.txt
assertEquals "chars - Accents (1-)"

for to in 44 45 46; do
    echo 'Quittant le wharf de l’île de Croÿ, le cœur déçu mais l’âme en joie, son fez brûlé sur la tête, la plutôt naïve Lætitia crapaüta en canoë au delà des Kerguelen, pour s’exiler où ? Près du mälström !' | ./ucut -b 30:$to | hex > result.txt
    echo 'Quittant le wharf de l’île de Croÿ, le cœur déçu mais l’âme en joie, son fez brûlé sur la tête, la plutôt naïve Lætitia crapaüta en canoë au delà des Kerguelen, pour s’exiler où ? Près du mälström !' | cut -b 30-$to | hex > expected.txt
    assertEquals "bytes - Accents (30-$to)"
done

echo "a;b;c" | ./ucut -d';' -f 1,1: > result.txt
echo "a;a;b;c" > expected.txt
assertEquals "fields - Add column at beginning"

printf "a;b;c\r\n" | ./ucut -d';' -f 1:,1 > result.txt
echo "a;b;c;a" > expected.txt
assertEquals "fields - carriage return"
