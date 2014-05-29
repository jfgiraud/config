#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import bs4
import codecs
import collections
import shutil
import lxml.html
import hashlib
import http.cookiejar
import locale
import os.path
import re
import sys
import textwrap
import urllib
import urllib.request
import urllib.parse
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed

def fix_url(url, current_url=None):
    if current_url:
        url = urllib.parse.urljoin(current_url, url)
    try:
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        for k, v in qs.items():
            if type(v) == type([]) and len(v) == 1:
                qs[k] = v[0].encode("latin-1")
        parsed_aslist = list(parsed)
        parsed_aslist[4] = urllib.parse.urlencode(qs)
        return urllib.parse.urlunparse(parsed_aslist)
    except:
        return url

def read_url(urlopener, url, encoding='latin1'):
    url = url.replace('&amp;', '&')
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


def parse_url(namespace, depth, url):
    page = read_url(None, url)
    for line in page.split('\n'):
        if line.startswith('<IMG SRC="/icons/folder.gif" ALT="[DIR]">'):
            line = line.replace('<IMG SRC="/icons/folder.gif" ALT="[DIR]"> <A HREF="', '')
            line = line[:line.find('/')]
            tourl = url + '/' + line
            if namespace.max_depth is not None and (depth + 1 > namespace.max_depth):
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
                    print(':: extension not accepted; ignore ' + href) 
                    continue
            (date, size) = (x.strip() for x in parsed[3].rsplit(' ', 1))
            if namespace.min_depth is not None and depth < namespace.min_depth:
                print(':: min depth not reached; ignore ' + href) 
            else:
                print(date + '|' + size + '|' + url + '/' + href)    

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 add_help=True,
                                 description='Create a file containing urls from an url')
    
parser.add_argument('url', metavar='URL', type=str, nargs=1, help='The url where performing operation')
parser.add_argument('--max-depth', metavar='LEVELS', type=int, help='Descend at mots levels')
parser.add_argument('--min-depth', metavar='LEVELS', type=int, help='Ignore file links at levels less than levels')
parser.add_argument('--accept', metavar='EXTENSIONS', type=str, help='Accept only the specified extensions')
#parser_extract.add_argument('--force', help="Force a default replace entry for all matches", action='store_true')
#parser_extract.add_argument('search', metavar='SEARCH', help='The string to search (ignoring case)')
#parser_extract.add_argument('replacement', metavar='REPLACEMENT', help='The string used to initialize values of the translation map')

if len(sys.argv)==1: 
    parser.print_help()
    sys.exit(1)

namespace = parser.parse_args()
print(namespace.max_depth)
try:
    parse_url(namespace, 0, namespace.url[0])
except KeyboardInterrupt:
    print('Interrupted.')
