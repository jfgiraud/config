#!/usr/bin/python3 -u

import getopt
import os
import re
import sys
import io
import tempfile
import shutil
import stat
import difflib

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
flag_extractmap = False
flag_detect = False
applymap = None

def error(message):
    print(message, file=sys.stderr)
    sys.exit(1)

def extract(fd):
    found = set()
    if flag_useregexp:
        reflags= re.I if flag_ignorecase else 0
        pattern = re.compile(search, reflags)
        for line in fd:
            found.update(pattern.findall(line))
        return found
    else:
        length = len(search)
        text = search.lower() if flag_ignorecase else search
        for line in fd:
            line2 = line.lower() if flag_ignorecase else line
            start = line2.find(text)
            while start >= 0:
                end = start + length
                found.add(line[start:end])
                start = line2.find(text, end)
        return found

def apply_on_file(file, pattern, repl):
    (use_stdout, filename) = file
    use_stdout = use_stdout or flag_simulate
    move = False
    with open(filename, 'rt') as fdin:
        if use_stdout:
            fdout = sys.stdout
        else:
            (fno, newfile) = tempfile.mkstemp()
            fdout = open(fno, 'wt')
            move = True
        with fdout:
            for line in fdin:
                if pattern:
                    line = re.sub(pattern, repl, line)
                fdout.write(line)
    if move:
        shutil.move(newfile, filename)

def compute_case(m, r):
    for f in [ 'upper', 'lower', 'title', 'capitalize' ]:
        if m == getattr(m, f)():
            return getattr(r, f)()
    return r

def extract_map(files):
    extracted = set()
    reflags= re.I if flag_ignorecase else 0
    for _, file in args:
        with open(file, 'rt') as fdin:
            extracted.update(extract(fdin))
    replacements = {}
    for match in extracted:
        #print(match)
        if type(match) == tuple:
            match = match[0]
        toreplace = re.sub(search, replace, match, flags=reflags)
        if flag_detect:
            #print('::', match, toreplace)
            s = difflib.SequenceMatcher(None, match, toreplace)
            cased = ''
            for op, i1, i2, j1, j2 in s.get_opcodes():
                #print(op, i1, i2, j1, j2)
                if op == 'equal':
                    cased = cased + toreplace[j1:j2]
                elif op == 'replace':
                    cased = cased + compute_case(match[i1:i2], toreplace[j1:j2])
                elif op == 'delete':
                    pass
                else: # insert
                    cased = cased + toreplace[j1:j2]
                # [('replace', 0, 6, 0, 7), ('equal', 6, 13, 7, 14), ('insert', 13, 13, 14, 16)]
            #print(':>', cased)

        replacements[match] = toreplace
    return replacements

try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:S:r:itea:d", ["help","search=","search-regexp=","replace=","ignore-case","simulate","extract-map","apply-map=","detect"])
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
    if o in ("-e", "--extract-map"):
        flag_extractmap = True
    if o in ("-a", "--apply-map"):
        applymap = a
    if o in ("-d", "--detect"):
        flag_detect = True

if flag_extractmap and flag_simulate:
    error("setting option --simulate makes no sense with option --extract-map") 

if flag_extractmap and applymap:
    error("--extract-map and --apply-map option are mutually exclusives") 

if flag_extractmap and (search is None or replace is None):
    error("setting option --extract-map implies to set options --search and --replace") 

if (applymap is None) and (search is None or replace is None):
    error("--search and --replace are required when --apply-map is not used")

def create_tmp_and_init(fdin):
    (fno, newfile) = tempfile.mkstemp() 
    with open(fno, 'wt') as fdout:
        for line in fdin:
            fdout.write(line)
    return newfile

def op(filename):
    if filename == '-':
        return (True, create_tmp_and_init(sys.stdin))
    else:
        with open(filename, 'rt') as fdin:
            if stat.S_ISFIFO(os.fstat(fdin.fileno()).st_mode):
                return (True, create_tmp_and_init(fdin))
            else:
                return (False, filename)

if len(args) == 0:
    args = [ "-" ]

args = [ op(x) for x in args ]

def apply_replacements(config):
    pattern = '|'.join(sorted(config, reverse=True))
    repl = lambda matchobj: config[matchobj.group(0)]
    for file in args:
        apply_on_file(file, pattern, repl)

if flag_extractmap:
    replacements = extract_map(args)
    for replacement in replacements:
        print(replacement, '=>', replacements[replacement])
elif applymap is not None:
    with open(applymap, 'rt') as fd:
        config = dict([(k.strip(),v.strip()) for (k,v) in [line.split(' => ', 2) for line in fd]])
    apply_replacements(config)
else:
    config = extract_map(args)
    apply_replacements(config)
