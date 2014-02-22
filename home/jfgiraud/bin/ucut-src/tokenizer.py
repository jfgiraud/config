#!/usr/bin/python

import shlex

def tokenize(t):
    result=[]
    spaces=(' ')
    quoted={"'":False,'"':False}
    w=''
    is_quoted=lambda: any([quoted[k] for k in quoted])
    quotes=quoted.keys()
    it=iter(t)
    for c in it:
        nextc=False
        while c == '\\':
            c=next(it)
            if not c:
                w=w+c
            elif c=='\\':
                w=w+'\\'
                nextc=True
                break
            elif c in quotes and is_quoted() and quoted[c]:
                w=w+c
                nextc=True
                break
            else:
                w=w+c
                nextc=True
                break
        if nextc:
            continue
        if c in spaces and not is_quoted():
            if w:
                result.append(w)
                w=''
        elif c in spaces and is_quoted():
            w=w+c
        elif c in quotes and not is_quoted():
            quoted[c]=True
            if w:
                result.append(w)
            w=c
        elif c in quotes and is_quoted():
            if not quoted[c]:
                w=w+c
            else:
                w=w+c
                quoted[c]=False
                result.append(w)
                w=''
        else:
            w=w+c
    if is_quoted():
        raise Exception('String sequence not closed!')
    if w:
        result.append(w)
    return result

def assertEquals(expected, text):
    result = tokenize(text)
    assert expected == result, "%s != %s" % (str(expected), str(result))
    print(result)


assertEquals([ 'abc' ], 'abc')
assertEquals([ '12', 'lorem', '34' ], '12 lorem 34')
assertEquals([ '12', '"lorem"', '34' ], '12 "lorem" 34') 
assertEquals([ '\'abc\'' ], '\'abc\'') # 'abc'
assertEquals([ '"abc"' ], '"abc"') # "abc"
assertEquals([ '"a\'bc"' ], '"a\'bc"') # "a'bc"
assertEquals([ '"ab"c"' ], '"ab\\"c"') # "ab"c"
assertEquals([ '"ab\\c"' ], '"ab\\\\c"') # "ab\c"
assertEquals([ '"ab"c"', 'def' ], '"ab\\"c" def') # "ab"c" def
assertEquals([ '"a\'bc"', 'def' ], '"a\'bc" def') # "a'bc" def
assertEquals([ '{', '"a"', '"*"', 'replace', '}' ], '{ "a" "*" replace }')
assertEquals([ '{', '"\\"', '"*"', 'replace', '}' ], '{ "\\\\" "*" replace }')
assertEquals([ '"abc defg"' ], '"abc defg"') 
assertEquals([ '"abc\\"' ], '"abc\\\\"') 
assertEquals([ '"abc\\""' ], '"abc\\\\\\""') 
assertEquals([ '"abc""' ], '"abc\\""') 
