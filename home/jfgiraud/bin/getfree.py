#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import argparse
import http.cookiejar
import re
import sys
import urllib
import urllib.request
import urllib.parse
import datetime
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL) 


# RAF 
# fmt

def read_url(no_messages, urlopener, url, encoding='latin1'):
    url = url.replace('&amp;', '&')
    if not no_messages:
        print(':: read ' + url, file=sys.stderr)
    try:
        if urlopener is None:
            response = urllib.request.urlopen(url)
        else:
            response = urlopener.open(url)
        content = response.readall()
        return content.decode(encoding)
    except Exception as e:
        #import traceback
        #traceback.print_exc()
        raise Exception('Erreur lors de la récupération de %s' % url)

def csize(s):
    if s[-1]=='k':
        return int(float(s[:-1])*1024)
    elif s[-1]=='M':
        return int(float(s[:-1])*1024*1024)
    else:
        return int(s)

def parse_url(namespace, depth, url):
    page = read_url(namespace.no_messages, None, url)
    for line in page.split('\n'):
        if line.startswith('<IMG SRC="/icons/folder.gif" ALT="[DIR]">'):
            line = line.replace('<IMG SRC="/icons/folder.gif" ALT="[DIR]"> <A HREF="', '')
            line = line[:line.find('/')]
            tourl = url + '/' + line
            if namespace.max_depth is not None and (depth + 1 > namespace.max_depth):
                if not namespace.no_messages:
                    print(':: max depth reached; ignore ' + tourl) 
            elif 'http://' not in line:
                parse_url(namespace, depth+1, tourl)
            continue

        pattern = '<IMG SRC="/icons/([\w\.]+)" ALT="\[([\w ]+)\]">'
        m = re.match(pattern, line)
        if m:
            icon = m.group(1)
            if icon == 'back.gif':
                continue
            parsed = [ x.strip() for x in line.split('>') ]
            href = url + '/' + parsed[1][9:-1]
            if namespace.accept is not None:
                ok = any([href.endswith('.'+x) for x in namespace.accept.split(',')])
                if not ok:
                    if not namespace.no_messages:
                        print(':: extension not accepted; ignore ' + href, file=sys.stderr) 
                    continue
            if namespace.reject is not None:
                ok = any([href.endswith('.'+x) for x in namespace.reject.split(',')])
                if ok:
                    if not namespace.no_messages:
                        print(':: extension not accepted; ignore ' + href, file=sys.stderr) 
                    continue
            (date, size) = (x.strip() for x in parsed[3].rsplit(' ', 1))
            if namespace.min_size is not None:
                bsize = csize(size)
                msize = csize(namespace.min_size)
                if bsize < msize:
                    if not namespace.no_messages:
                        print(':: file too small [%s]; ignore %s' % (size, href), file=sys.stderr) 
                    continue
            if namespace.max_size is not None:
                bsize = csize(size)
                msize = csize(namespace.max_size)
                if bsize > msize:
                    if not namespace.no_messages:
                        print(':: file too large [%s]; ignore %s' % (size, href), file=sys.stderr) 
                    continue
            if namespace.min_depth is not None and depth < namespace.min_depth:
                if not namespace.no_messages:
                    print(':: min depth not reached; ignore ' + href, file=sys.stderr) 
                continue
            if namespace.before is not None:
                bdate = datetime.datetime.strptime(date, '%d-%b-%Y %H:%M')
                mdate = datetime.datetime.strptime(namespace.before, '%Y-%m-%d %H:%M')
                if bdate > mdate:
                    if not namespace.no_messages:
                        print(':: date [%s] after [%s]; ignore %s' % (bdate, mdate, href), file=sys.stderr) 
                    continue
            if namespace.after is not None:
                bdate = datetime.datetime.strptime(date, '%d-%b-%Y %H:%M')
                mdate = datetime.datetime.strptime(namespace.after, '%Y-%m-%d %H:%M')
                if bdate < mdate:
                    if not namespace.no_messages:
                        print(':: date [%s] before [%s]; ignore %s' % (bdate, mdate, href), file=sys.stderr) 
                    continue
            print(date + '|' + size + '|' + url + '/' + href)    

def size_string(v):
    try:
        return re.match("^\d+(\.\d+)?[kM]?", v).group(0)
    except:
        raise ArgumentTypeError("String '%s' does not match required format" % (v,))

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 add_help=True,
                                 description='Create a file containing urls from an url')
    
parser.add_argument('url', metavar='URL', type=str, nargs=1, help='The url where performing operation')
parser.add_argument('--max-depth', metavar='LEVELS', type=int, help='Descend at mots levels')
parser.add_argument('--min-depth', metavar='LEVELS', type=int, help='Ignore file links at levels less than levels')
parser.add_argument('--min-size', metavar='SIZE', type=size_string, help='Ignore file with size less than the specified size')
parser.add_argument('--max-size', metavar='SIZE', type=size_string, help='Ignore file with size greater than the specified size')
parser.add_argument('--accept', metavar='EXTENSIONS', type=str, help='Accept only the files with the specified extensions')
parser.add_argument('--reject', metavar='EXTENSIONS', type=str, help='Reject the files with the specified extensions')
parser.add_argument('--no-messages', help='Suppress messages', action='store_true')
parser.add_argument('--after', metavar='DATETIME', type=str, help='Reject the files with date/time before the specified datetime (YYYY-MM-DD hh:mm)')
parser.add_argument('--before', metavar='DATETIME', type=str, help='Reject the files with date/time after the specified datetime (YYYY-MM-DD hh:mm)')
#parser_extract.add_argument('--force', help="Force a default replace entry for all matches", action='store_true')
#parser_extract.add_argument('search', metavar='SEARCH', help='The string to search (ignoring case)')
#parser_extract.add_argument('replacement', metavar='REPLACEMENT', help='The string used to initialize values of the translation map')

if len(sys.argv)==1: 
    parser.print_help()
    sys.exit(1)

namespace = parser.parse_args()
try:
    parse_url(namespace, 0, namespace.url[0])
except KeyboardInterrupt:
    print('Interrupted.')
