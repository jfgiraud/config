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


def parse_url(url):
    page = read_url(None, url)
    for line in page.split('\n'):
        if line.startswith('<IMG SRC="/icons/folder.gif" ALT="[DIR]">'):
            line = line.replace('<IMG SRC="/icons/folder.gif" ALT="[DIR]"> <A HREF="', '')
            line = line[:line.find('/')]
            if 'http://' not in line:
                parse_url(url + '/' + line)
        else:
            pattern = '<IMG SRC="/icons/([\w\.]+)" ALT="\[([\w ]+)\]">'
            m = re.match(pattern, line)
            if m:
                icon = m.group(1)
                if icon == 'back.gif':
                    continue
                parsed = [ x.strip() for x in line.split('>') ]
                href = parsed[1][9:-1]
                (date, size) = (x.strip() for x in parsed[3].rsplit(' ', 1))
                print(date + '|' + size + '|' + url + '/' + href)

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 add_help=True,
                                 description='Create a file containing urls from an url')

#parser_extract.add_argument('--force', help="Force a default replace entry for all matches", action='store_true')
#parser_extract.add_argument('search', metavar='SEARCH', help='The string to search (ignoring case)')
#parser_extract.add_argument('replacement', metavar='REPLACEMENT', help='The string used to initialize values of the translation map')
parser.add_argument('url', metavar='URL', type=str, nargs=1, help='The url where performing operation')

if len(sys.argv)==1: 
    parser.print_help()
    sys.exit(1)

namespace = parser.parse_args()

try:
    parse_url(namespace.url[0])
except KeyboardInterrupt:
    print('Interrupted.')