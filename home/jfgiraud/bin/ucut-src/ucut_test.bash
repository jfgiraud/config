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
        echo == expects:
	echo
        cat expected.txt
	echo
        echo == but receives:
	echo
        cat result.txt
	echo
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

echo "élo" | ./ucut -c 1 | hexdump -ve '1/1 "%.2x"' > result.txt
echo "élo" | cut -c 1 | hexdump -ve '1/1 "%.2x"' > expected.txt
assertEquals "chars - Accents (1)"

echo "élo" | ./ucut -c '1:' | hexdump -ve '1/1 "%.2x"' > result.txt
echo "élo" | cut -c '1-' | hexdump -ve '1/1 "%.2x"' > expected.txt
assertEquals "chars - Accents (1-)"

for to in 44 45 46; do
    echo 'Quittant le wharf de l’île de Croÿ, le cœur déçu mais l’âme en joie, son fez brûlé sur la tête, la plutôt naïve Lætitia crapaüta en canoë au delà des Kerguelen, pour s’exiler où ? Près du mälström !' | ./ucut -b 30:$to | hexdump -e '1/1 "%.2x"' > result.txt
    echo 'Quittant le wharf de l’île de Croÿ, le cœur déçu mais l’âme en joie, son fez brûlé sur la tête, la plutôt naïve Lætitia crapaüta en canoë au delà des Kerguelen, pour s’exiler où ? Près du mälström !' | cut -b 30-$to | hexdump -e '1/1 "%.2x"' > expected.txt
    assertEquals "bytes - Accents (30-$to)"
done

for i in $(seq 1 100); do
    (cat <<EOF
"1","01","ozan","OZAN","Ozan","O250","OSN","01190","284","01284","2","26","6","618","469","500","94","660","4.91667","46.3833","2866","51546","+45456","462330","170","205","14126","8823","26916"
"2","01","cormoranche-sur-saone","CORMORANCHE-SUR-SAONE","Cormoranche-sur-Saône","C65652625","KRMRNXSRSN","01290","123","01123","2","27","6","1058","903","1000","107","985","4.83333","46.2333","2772","51379","+44953","461427","168","211","9070","7767","19911"
"3","01","plagne-01","PLAGNE","Plagne","P425","PLKN","01130","298","01298","4","03","6","129","83","100","21","620","5.73333","46.1833","3769","51324","+54342","461131","560","922","31104","25594","27923"
EOF
) >> given.txt
done

(cat <<EOF
OSN;OZAN
KRMRNXSRSN;CORMORANCHE-SUR-SAONE
PLKN;PLAGNE
OSN;OZAN
KRMRNXSRSN;CORMORANCHE-SUR-SAONE
PLKN;PLAGNE
OSN;OZAN
KRMRNXSRSN;CORMORANCHE-SUR-SAONE
PLKN;PLAGNE
OSN;OZAN
EOF
) > expected.txt

(./ucut -d ',' -s -f $'(4,7)@{ { -> d { d "\\"" "" replace } } q sto q eval swap q eval 2 ->list "{0};{1}" swap format }' given.txt | head -n 10) &> result.txt

assertEquals "pipes"