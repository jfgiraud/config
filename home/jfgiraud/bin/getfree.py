#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import argparse
import http.cookiejar
import os
import re
import sys
import urllib
import urllib.request
import urllib.parse
import shutil
import datetime
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL) 


# RAF 
# fmt

def print_err(no_messages, text):
    if not no_messages:
        print(text, file=sys.stderr)


def read_url(no_messages, urlopener, url, encoding='latin1'):
    url = url.replace('&amp;', '&')
    print_err(namespace.no_messages, ':: read ' + url)
    try:
        if urlopener is None:
            response = urllib.request.urlopen(url)
        else:
            response = urlopener.open(url)
        content = response.readall()
        return content.decode(encoding)
    except Exception as e:
        raise Exception('Error while trying to read url %s' % url)


def size_str_2_int(s):
    if s[-1]=='k':
        return int(float(s[:-1])*1024)
    elif s[-1]=='M':
        return int(float(s[:-1])*1024*1024)
    else:
        return int(s)

def humanize_size(s):
    if re.match('^\d+$', s):
        s=int(s)
        if s>=1024:
            s=s//1024
            x='k'
        if s>=1024:
            s=s//1024
            x='M'
        return '%d%s' % (s, x)
    return s

class Conf:
    
    def __init__(self, dir_regex, a_regex, date_fmt, line_sep):
        self.DIR_REGEX = re.compile(dir_regex, re.IGNORECASE)
        self.A_REGEX = re.compile(a_regex, re.IGNORECASE)
        self.LINE_SEP = line_sep
        self.DATE_FMT = date_fmt
        self.DATE_REGEXP = re.compile(a2regexp(date_fmt), re.IGNORECASE)

    def a_regexp(self):
        return self.A_REGEX

    def dir_regexp(self):
        return self.DIR_REGEX

    def date_regexp(self):
        return self.DATE_REGEXP

    def date_strptime(self):
        if self.DATE_FMT:
            return a2strptime(self.DATE_FMT)
        else:
            return None


def range_padded(s,n,l=2):
    return '(' + '|'.join([str(x).zfill(l) for x in range(s,n+1)]) + ')'

def a2regexp(f):
    f = f.replace('DD', range_padded(1,31))
    f = f.replace('D', range_padded(1,31,1))
    f = f.replace('MMM', '\w+')
    f = f.replace('MM', range_padded(1,12))
    f = f.replace('M', range_padded(1,12,1))
    f = f.replace('YYYY', '([12][0-9]{3})')
    f = f.replace('HH', range_padded(0,23))
    f = f.replace('H', range_padded(0,23,1))
    f = f.replace('hh', range_padded(1,12))
    f = f.replace('h', range_padded(1,12,1))
    f = f.replace('A', '(AM|PM)')
    f = f.replace('a', '(am|pm)')
    f = f.replace('mm', range_padded(0,59))
    f = f.replace('m', range_padded(0,59,1))
    f = f.replace(' ', '\s+')
    return '.*(' + f + ').*'

def a2strptime(f):
    h = {
        'DD': '%d',
        'D': '%d',
        'MMM': '%b',
        'MM': '%m',
        'M': '%m',
        'YYYY': '%Y',
        'HH': '%H',
        'H': '%H',
        'hh': '%I',
        'h': '%I',
        'A': '%p',
        'a': '%p',
        'mm': '%M',
        'm': '%M'
    }
    keys = [ (len(x), x) for x in h ]
    keys.sort()
    keys.reverse()
    return re.sub('|'.join([b for a,b in keys]), lambda matchobj: h[matchobj.group(0)], f)

def detect_conf(page):
    page = page.replace('\n', '')
    formats = [ 'DD-MMM-YYYY HH:mm', 'M/D/YYYY h:mm A', 'YYYY-MM-DD HH:mm' ]
    date_fmt = next((fmt for fmt in formats if re.match(a2regexp(fmt), page, re.IGNORECASE)), None)
    if date_fmt is None:
        print('Date format not detected.', file=sys.stderr)
        sys.exit(1)
    line_sep = '<br>' if re.match('.*</a><br>.*', page, re.IGNORECASE) else '\n'
    return Conf('<a href="([^"]*/)">[^<]*</a>', 
                '<a href="([^"]*[^\/])">[^<]*</a>', 
                date_fmt, 
                line_sep)

CLEAN_LINE = [ re.compile('\s*<img[^>]+>\s*', re.IGNORECASE),
               re.compile('\s*<a[^>]+>[^<]*</a>\s*', re.IGNORECASE)
]

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
    
def parse_url(namespace, depth, url, conf=None, count=1):
    page = read_url(namespace.no_messages, None, url)
    if not 'Parent Directory' in page:
        return
    if conf is None:
        conf = detect_conf(page)
    for line in page.split(conf.LINE_SEP):
        if 'Parent Directory' in line or 'Last modified' in line:
            continue
        search = conf.dir_regexp().search(line)
        if search:
            line = search.group(1)
            tourl = url + '/' + line
            if namespace.max_depth is not None and (depth + 1 > namespace.max_depth):
                print_err(namespace.no_messages, ':: max depth reached; ignore ' + tourl) 
            elif 'http://' not in line:
                count = parse_url(namespace, depth+1, tourl, conf, count)
            continue
        search = conf.a_regexp().search(line)
        date = conf.date_regexp().search(line)
        if date:
            date = date.group(1)
        if search and date:
            tourl = search.group(1)
            #href = url + '/' + tourl
            href = fix_url(tourl, url)
            for regex in CLEAN_LINE:
                line = regex.sub('', line)
            line = line.replace(date, '')
            size = line.strip()
            if check_entry(date, size, href, conf):
                if is_between_lines(namespace, count):
                    date = datetime.datetime.strptime(date, conf.date_strptime())
                    date = date.strftime('%Y-%m-%d %H:%M')
                    size = humanize_size(size)
                    execute(date, size, href, count)
                else:
                    print_err(namespace.no_messages, ":: not in range (#" + str(count) + "); ignore " + tourl)
                count = count + 1
    return count

def print_separator(text):
    columns = shutil.get_terminal_size().columns
    print('-- ' + text + ' ' + '-' * (columns - len(text) - 5), file=sys.stdout)

def execute(date, size, href, count):
    if namespace.print or namespace.exec:
        banner = '#{index} {date} [{size}] {url}'.format(index=count, size=size, date=date, url=href)
        if namespace.print:
            print_separator(namespace.print.format(index=count, size=size, date=date, url=href, banner=banner))
        if namespace.exec:
            os.system(namespace.exec.format(index=count, size=size, date=date, url=href, banner=banner))
    else:
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
            print_err(namespace.no_messages, ':: extension not accepted; ignore ' + href) 
            return 0
    if namespace.reject is not None:
        ok = any([href.endswith('.'+x) for x in namespace.reject.split(',')])
        if ok:
            print_err(namespace.no_messages, ':: extension not accepted; ignore ' + href) 
            return 0
    if namespace.min_size is not None:
        bsize = size_str_2_int(size)
        msize = size_str_2_int(namespace.min_size)
        if bsize < msize:
            print_err(namespace.no_messages, ':: file too small [%s]; ignore %s' % (size, href)) 
            return 0
    if namespace.max_size is not None:
        bsize = size_str_2_int(size)
        msize = size_str_2_int(namespace.max_size)
        if bsize > msize:
            print_err(namespace.no_messages, ':: file too large [%s]; ignore %s' % (size, href)) 
            return 0
    if namespace.min_depth is not None and depth < namespace.min_depth:
        print_err(namespace.no_messages, ':: min depth not reached; ignore ' + href) 
        return 0
    if namespace.before is not None:
        bdate = datetime.datetime.strptime(date, conf.date_strptime())
        mdate = datetime.datetime.strptime(namespace.before, '%Y-%m-%d %H:%M')
        if bdate > mdate:
            print_err(namespace.no_messages, ':: date [%s] after [%s]; ignore %s' % (bdate, mdate, href)) 
            return 0
    if namespace.after is not None:
        bdate = datetime.datetime.strptime(date, conf.date_strptime())
        mdate = datetime.datetime.strptime(namespace.after, '%Y-%m-%d %H:%M')
        if bdate < mdate:
            print_err(namespace.no_messages, ':: date [%s] before [%s]; ignore %s' % (bdate, mdate, href)) 
            return 0
    return 1

def is_between_lines(namespace, c):
    if namespace.lines != None:
        o = re.match("(\d+)?(-)?(\d+)?", namespace.lines)
        if o.group(2) == '-':
            (start, end) = (o.group(1), o.group(3))
        else:
            (start, end) = (o.group(1), o.group(1))
        if (start is not None) and (c < int(start)):
            return False      
        if (end is not None) and (c > int(end)):
            return False
    return True

def parse_file(namespace, file, count=1):
    print_err(namespace.no_messages, ':: read ' + file)
    with open(file, 'r') as fd:
        content = fd.read()
    conf = detect_conf(content)
    with open(file, 'r') as fd:
        for line in fd:
            line = line[:-1]
            (date, size, href) = line.split('|', 3)
            if check_entry(date, size, href, conf):
                if is_between_lines(namespace, count):
                    execute(date, size, href, count)
                else:
                    print_err(namespace.no_messages, ":: not in range (#" + str(count) + "); ignore " + href)
                count = count + 1

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
    a_parser.add_argument('--lines', metavar='LINES', type=str, help='Select specified lines matching all filters (N, N-, N-M, -M)')
    a_parser.add_argument('--print', metavar='FORMAT', type=str, help='Print the given string replacing patterns {index} {date} {size} {url} {banner} by their respective values")')
    a_parser.add_argument('--exec', metavar='COMMAND', type=str, help='Execute the given shell command (ex: echo "#{index} {date} // {size} // {url}")')

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
