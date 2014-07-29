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
        raise Exception('Error while trying to read url %s' % url)

def csize(s):
    if s[-1]=='k':
        return int(float(s[:-1])*1024)
    elif s[-1]=='M':
        return int(float(s[:-1])*1024*1024)
    else:
        return int(s)

class Conf:
    
    def __init__(self, dir_regex, a_regex, date_fmt, line_sep):
        self.DIR_REGEX = re.compile(dir_regex, re.IGNORECASE)
        self.A_REGEX = re.compile(a_regex, re.IGNORECASE)
        self.DATE_FMT = date_fmt
        self.LINE_SEP = line_sep


def xxx(s,n,l=2):
    return '(' + '|'.join([str(x).zfill(l) for x in range(s,n+1)]) + ')'

def y(f):
    f = f.replace('DD', xxx(1,31))
    f = f.replace('D', xxx(1,31,1))
    f = f.replace('MMM', '\w+')
    f = f.replace('MM', xxx(1,12))
    f = f.replace('M', xxx(1,12,1))
    f = f.replace('YYYY', '([12][0-9]{3})')
    f = f.replace('HH', xxx(0,23))
    f = f.replace('H', xxx(0,23,1))
    f = f.replace('hh', xxx(1,12))
    f = f.replace('h', xxx(1,12,1))
    f = f.replace('A', '(AM|PM)')
    f = f.replace('a', '(am|pm)')
    f = f.replace('mm', xxx(0,59))
    f = f.replace('m', xxx(0,59,1))
    f = f.replace(' ', '\s+')
    return '.*' + f + '.*'

def detect_conf(page):
    page = page.replace('\n', '')
    date_fmt = next((fmt for fmt in [ y('DD-MMM-YYYY HH:mm'), y('M/D/YYYY h:mm A') ] if re.match(fmt, page, re.IGNORECASE)), None)
    #print(",,,,",date_fmt)
    #print(re.match(date_fmt, page.replace('\n',''), re.IGNORECASE))
    line_sep = '<br>' if re.match('.*</a><br>.*', page, re.IGNORECASE) else '\n'
    #line_sep = '\n'
    print(',,,,',line_sep)
    return Conf('<a href="([^"]*/)">[^<]*</a>', 
                '<a href="([^"]*[^\/])">[^<]*</a>', 
                date_fmt, 
                line_sep)
    
def parse_url(namespace, depth, url, conf=None):
    page = read_url(namespace.no_messages, None, url)
    if not 'Parent Directory' in page:
        return
    if conf is None:
        conf = detect_conf(page)
    for line in page.split(conf.LINE_SEP):
        if 'Parent Directory' in line or 'Last modified' in line:
            continue
        search = conf.DIR_REGEX.search(line)
        if search:
            line = search.group(1)
            tourl = url + '/' + line
            if namespace.max_depth is not None and (depth + 1 > namespace.max_depth):
                if not namespace.no_messages:
                    print(':: max depth reached; ignore ' + tourl) 
            elif 'http://' not in line:
                parse_url(namespace, depth+1, tourl, conf)
            continue
        search = conf.A_REGEX.search(line)
        if search:
            parsed = [ x.strip() for x in line.split('>') ]
            tourl = search.group(1)
            href = url + '/' + tourl
            (date, size) = (x.strip() for x in parsed[-1].rsplit(' ', 1))
            if check_entry(date, size, href, conf):
                print(date + '|' + size + '|' + href)    

def size_string(v):
    try:
        return re.match("^\d+(\.\d+)?[kM]?", v).group(0)
    except:
        raise ArgumentTypeError("String '%s' does not match required format" % (v,))

def check_entry(date, size, href, conf):
    if namespace.accept is not None:
        ok = any([href.endswith('.'+x) for x in namespace.accept.split(',')])
        if not ok:
            if not namespace.no_messages:
                print(':: extension not accepted; ignore ' + href, file=sys.stderr) 
            return 0
    if namespace.reject is not None:
        ok = any([href.endswith('.'+x) for x in namespace.reject.split(',')])
        if ok:
            if not namespace.no_messages:
                print(':: extension not accepted; ignore ' + href, file=sys.stderr) 
            return 0
    if namespace.min_size is not None:
        bsize = csize(size)
        msize = csize(namespace.min_size)
        if bsize < msize:
            if not namespace.no_messages:
                print(':: file too small [%s]; ignore %s' % (size, href), file=sys.stderr) 
            return 0
    if namespace.max_size is not None:
        bsize = csize(size)
        msize = csize(namespace.max_size)
        if bsize > msize:
            if not namespace.no_messages:
                print(':: file too large [%s]; ignore %s' % (size, href), file=sys.stderr) 
            return 0
    if namespace.min_depth is not None and depth < namespace.min_depth:
        if not namespace.no_messages:
            print(':: min depth not reached; ignore ' + href, file=sys.stderr) 
        return 0
    if namespace.before is not None:
        bdate = datetime.datetime.strptime(date, conf.DATE_FMT)
        mdate = datetime.datetime.strptime(namespace.before, '%Y-%m-%d %H:%M')
        if bdate > mdate:
            if not namespace.no_messages:
                print(':: date [%s] after [%s]; ignore %s' % (bdate, mdate, href), file=sys.stderr) 
            return 0
    if namespace.after is not None:
        bdate = datetime.datetime.strptime(date, conf.DATE_FMT)
        mdate = datetime.datetime.strptime(namespace.after, '%Y-%m-%d %H:%M')
        if bdate < mdate:
            if not namespace.no_messages:
                print(':: date [%s] before [%s]; ignore %s' % (bdate, mdate, href), file=sys.stderr) 
            return 0
    return 1

def parse_file(namespace, file):
    if not namespace.no_messages:
        print(':: read ' + file, file=sys.stderr)
    with open(file, 'r') as fd:
        content = fd.read()
    conf = detect_conf(content)
    with open(file, 'r') as fd:
        for line in fd:
            line = line[:-1]
            (date, size, href) = line.split('|', 3)
            if check_entry(date, size, href, conf):
                print(date + '|' + size + '|' + href)    


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 add_help=True,
                                 description='Parent Directory Indexor: scan an homedir and create a file containing urls')

subparsers = parser.add_subparsers(help='Help for subcommand', dest='command')

parser_url = subparsers.add_parser('url', help='Scan an url and follow links to create a file containing urls')
parser_url.add_argument('url', metavar='URL', type=str, nargs=1, help='The url where performing operation')

parser_file = subparsers.add_parser('file', help='Scan a file containing urls to filter items')
parser_file.add_argument('file', metavar='FILE', type=str, nargs=1, help='The file on which perform operation')

for a_parser in [ parser_url, parser_file ]:
    a_parser.add_argument('--max-depth', metavar='LEVELS', type=int, help='Descend at mots levels')
    a_parser.add_argument('--min-depth', metavar='LEVELS', type=int, help='Ignore file links at levels less than levels')
    a_parser.add_argument('--min-size', metavar='SIZE', type=size_string, help='Ignore file with size less than the specified size')
    a_parser.add_argument('--max-size', metavar='SIZE', type=size_string, help='Ignore file with size greater than the specified size')
    a_parser.add_argument('--accept', metavar='EXTENSIONS', type=str, help='Accept only the files with the specified extensions')
    a_parser.add_argument('--reject', metavar='EXTENSIONS', type=str, help='Reject the files with the specified extensions')
    a_parser.add_argument('--no-messages', help='Suppress messages', action='store_true')
    a_parser.add_argument('--after', metavar='DATETIME', type=str, help='Reject the files with date/time before the specified datetime (YYYY-MM-DD hh:mm)')
    a_parser.add_argument('--before', metavar='DATETIME', type=str, help='Reject the files with date/time after the specified datetime (YYYY-MM-DD hh:mm)')

if len(sys.argv)==1: 
    parser.print_help()
    sys.exit(1)



namespace = parser.parse_args()
try:
    if namespace.command == 'url':
        parse_url(namespace, 0, namespace.url[0])
    else:
        parse_file(namespace, namespace.file[0])
except KeyboardInterrupt:
    print('Interrupted.', file=sys.stderr)
