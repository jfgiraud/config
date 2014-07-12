#!/usr/bin/python

import getopt
import sys

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
 *********************************************
             -i, --ignore-case    search ingoring case
             -a, --apply-map      use a map to perform replacement
             -t, --simulate       perform a simulation for replacements
                                  the results will be displayed on standart output
             -c, --confirm        prompt before applaying replacements on files
                                  
        
With no FILE, or when FILE is -, read standard input.

AUTHOR
	Written by Jean-Francois Giraud.

COPYRIGHT
	Copyright (c) 2012-2014 Jean-François Giraud.  
	License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
	This is free software: you are free to change and redistribute it.  
	There is NO WARRANTY, to the extent permitted by law.
    ''' % {'prog': sys.argv[0]})
    sys.exit(retval)


search=None
replace=None
use_regexp=False
ignorecase=False

# GetOptions (
# 	    'ignore-case|i' => \$ignorecase,
# 	    'simulate|t' => \$simulate,
# 	    'confirm|c' => \$confirm,
# 	    'extract-map|e' => \$extract_map,
# 	    'compute-case-method|m=s' => \$algorithm,
# 	    'apply-map|a=s' => sub { $apply_map=1; $map_file=$_[1] },


try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:S:r:i", ["help","search=","search-regexp=","replace=","ignore-case"])
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
        use_regexp = True
    if o in ("-i", "--ignore-case"):
        ignorecase = True

usage(0)
