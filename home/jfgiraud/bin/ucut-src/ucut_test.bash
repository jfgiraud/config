#!/bin/bash

# bug : ucut -d ',' -s -f $'(4,7)@{ { -> d { d "\\"" "" replace } } q sto q eval swap q eval 2 ->list "{0};{1}"  }' ./villes_france.csv |head
#       produit IOError: [Errno 32] Broken pipe
#
# bug : echo "élo" | ./ucut -f 1
#       retour chariot en trop


function assertEquals() {
    echo -n ":: $1: "
    if ! diff result.txt expected.txt > /dev/null; then
        echo "KO"
        echo expects:
        cat expected.txt
        echo but receives:
        cat result.txt
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
assertEquals "fields - Delimiter with accent"

echo "élo" | ./ucut -c 1 > result.txt
echo "é" > expected.txt
assertEquals "chars - No new line"
