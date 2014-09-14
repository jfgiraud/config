#!/usr/bin/python3

import getopt
import os
import re
import sys

# python sandr.py -e -S '((\w+)jour)' -r 'helLO\1' -i aaa
# python sandr.py -e -s BONjour -r helLO -i aaa
# bug python sandr.py -e -s '((\w+)jour)' -r 'helLO\1' -i aaa

def usage(retval=0):
    print('''NAME:

        %(prog)s - perform pattern replacement in files

SYNOPSYS:

        %(prog)s
             -h, --help           display help
             -s, --search         the string to search
             -S, --search-regexp  the pattern to search
             -r, --replace        the string (or the pattern) used to replace all matches 
             -e, --extract-map    extract from file or standart input all matches of searched
                                  string or pattern.
                                  a map created with found matches is displayed on standart 
                                  output. entries of this map will be setted with a default
                                  value
             -i, --ignore-case    search ingoring case
             -a, --apply-map      use a map to perform replacement
             -t, --simulate       perform a simulation for replacements
                                  the results will be displayed on standart output
####             -c, --confirm        prompt before applaying replacements on files
                                  
        
With no FILE, or when FILE is -, read standard input.

AUTHOR
	Written by Jean-François Giraud.

COPYRIGHT
	Copyright (c) 2012-2014 Jean-François Giraud.  
	License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
	This is free software: you are free to change and redistribute it.  
	There is NO WARRANTY, to the extent permitted by law.
    ''' % {'prog': sys.argv[0]})
    sys.exit(retval)

search = None
replace = None
flag_useregexp = False
flag_ignorecase = False
flag_simulate = False
###flag_confirm = False
flag_extractmap = False
applymap = None
algorithm = None

def compute_case(m,s,r, flag_useregexp):
    if s == m:
        return r
    if s == m.swapcase():
        return r.swapcase()
    for f in [ 'lower', 'upper', 'capitalize', 'title' ]:
        if m == getattr(m, f)():
            return getattr(r, f)()
    return r

algorithms = { 'id': lambda m,s,r: r,
               'default_extract': compute_case
}

try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:S:r:iscea:m:", ["help","search=","search-regexp=","replace=","ignore-case","simulate","confirm","extract-map","apply-map=","method="])
except getopt.GetoptError:
    usage(2)

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
    if o in ("-s", "--search"):
        search = a
    if o in ("-r", "--replace"):
        replace = a
    if o in ("-S", "--search-regexp"):
        search = a
        flag_useregexp = True
    if o in ("-i", "--ignore-case"):
        flag_ignorecase = True
    if o in ("-t", "--simulate"):
        flag_simulate = True
###    if o in ("-c", "--confirm"):
###        flag_confirm = True
    if o in ("-e", "--extract-map"):
        flag_extractmap = True
    if o in ("-a", "--apply-map"):
        applymap = a

def error(message):
    print(message, file=sys.stderr)
    sys.exit(1)

if flag_extractmap and flag_simulate:
    error("setting option --simulate makes no sense with option --extract-map") 

###if flag_extractmap and flag_confirm:
###    error("setting option --confirm makes no sense with option --extract-map") 

if flag_extractmap and applymap:
    error("--extract-map and --apply-map option are mutually exclusives") 

if flag_extractmap and (search is None or replace is None):
    error("setting option --extract-map implies to set options --search and --replace") 

if (applymap is None) and (search is None or replace is None):
    error("--search and --replace are required when --apply-map is not used")

if (algorithm is not None) and algorithm not in algorithms:
    error("unknown algorithm '%s' for option --compute-case-method" % (algorithm)) 

def extract(fdin):
    found = set()
    if flag_useregexp:
        reflags= re.I if flag_ignorecase else 0
        pattern = re.compile(search, reflags)
        for line in fdin:
            found.update(pattern.findall(line))
        return found
    else:
        length = len(search)
        text = search.lower() if flag_ignorecase else search
        for line in fdin:
            line2 = line.lower() if flag_ignorecase else line
            start = line2.find(text)
            while start >= 0:
                end = start + length
                found.add(line[start:end])
                start = line2.find(text, end)
        return found

if len(args) == 0:
    args = [ "-" ]

if flag_extractmap:
    extracted = set()
    reflags= re.I if flag_ignorecase else 0
    for file in args:
        with sys.stdin if file == '-' else open(file, 'rt') as fdin:
            extracted.update(extract(fdin))
    method = algorithms.get(algorithm, algorithms['default_extract'])
    for match in extracted:
        if not flag_useregexp:
            toreplace = re.sub(search, replace, match, flags=reflags)
            print(match, '=>', method(match, search, toreplace, flag_useregexp))
        else:
            #if type(match)==tuple:
            #    match = match[0]
            toreplace = re.sub(search, replace, match, flags=reflags)
            print(match, '=>', method(match, search, toreplace, flag_useregexp))
elif applymap is not None:
    with open(applymap, 'rt') as fd:
        config = dict([(k.strip(),v.strip()) for (k,v) in [line.split(' => ', 2) for line in fd]])
    print(config)
else:
    raise Exception('à implémenter')
