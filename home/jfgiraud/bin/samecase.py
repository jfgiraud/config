#!/usr/bin/python3

from difflib import *
import sys

x, y = sys.argv[1], sys.argv[2]
s, t = x.lower(), y.lower()

opts = [x for x in SequenceMatcher(None, s, t).get_matching_blocks()]
i1, j1 = 0, 0
d = int(sys.argv[3])
res = [ [], [] ]
while opts:
    i2, j2, size = opts.pop(0) 
    #print(i2, j2, size)
    if size == 0:
        res[0].append(x[i1:])
        res[1].append(y[j1:])
        break
    if size < d:
        continue
    res[0].append(x[i1:i2])
    res[1].append(y[j1:j2])
    res[0].append(x[i2:i2+size])
    res[1].append(y[j2:j2+size])
    i1 = i2+size
    j1 = j2+size
print(res)
