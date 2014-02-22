#!/usr/bin/python3

from stack import *

if __name__ == '__main__':

    def assertStackOp(expected, ret, elements, op, *args):
        assert type(expected) == type(elements)
        if type(expected) == tuple:
            egv = expected[1]
            elv = expected[2]
            expected = expected[0]
            igv = elements[1]
            ilv = elements[2]
            elements = elements[0]
        else:
            egv = {}
            elv = []
            igv = {}
            ilv = []
            
        e=Stack(expected)
        i=Stack(elements)
        i.g_variables = igv
        i.l_variables = ilv
        try:
            f=getattr(i, op)
            r=f(*args)
            #print type(i.value()), i.value()
            assert e == i, str(e) + ' != ' + str(i)
            assert egv == i.g_variables
            assert elv == i.l_variables
            assert r == ret
        except AssertionError as e:
            if ret is not None:
                assert ret.args[0] == e.args[0], e.args[0]
            else:
                raise e
        
    assertStackOp([7], None, [5,2], '_add')
    assertStackOp([3], None, [5,2], '_sub')
    assertStackOp([10], None, [5,2], '_mul')
    assertStackOp([2.5], None, [5,2], '_div')
    assertStackOp([1], None, [5,5], '_eq')
    assertStackOp([0], None, [5,7], '_eq')
    assertStackOp([0], None, [5,5], '_ne')
    assertStackOp([1], None, [5,7], '_ne')
    assertStackOp([0], None, [5,5], '_lt')
    assertStackOp([1], None, [5,7], '_lt')
    assertStackOp([0], None, [7,5], '_lt')
    assertStackOp([1], None, [5,5], '_le')
    assertStackOp([1], None, [5,7], '_le')
    assertStackOp([0], None, [7,5], '_le')
    assertStackOp([0], None, [5,5], '_gt')
    assertStackOp([0], None, [5,7], '_gt')
    assertStackOp([1], None, [7,5], '_gt')
    assertStackOp([1], None, [5,5], '_ge')
    assertStackOp([0], None, [5,7], '_ge')
    assertStackOp([1], None, [7,5], '_ge')

    assertStackOp([True], None, [True,True], '_and')
    assertStackOp([False], None, [True,False], '_and')
    assertStackOp([False], None, [False,True], '_and')
    assertStackOp([False], None, [False,False], '_and')
    assertStackOp([True], None, [True,True], '_or')
    assertStackOp([True], None, [True,False], '_or')
    assertStackOp([True], None, [False,True], '_or')
    assertStackOp([False], None, [False,False], '_or')
    assertStackOp([True], None, [False], '_not')
    assertStackOp([False], None, [True], '_not')
    assertStackOp([False], None, [True,True], '_xor')
    assertStackOp([True], None, [True,False], '_xor')
    assertStackOp([True], None, [False,True], '_xor')
    assertStackOp([False], None, [False,False], '_xor')

    assertStackOp(["a"], None, [True,"a"], 'ift')
    assertStackOp([], None, [False,"a"], 'ift')
    assertStackOp(["a", "b"], AssertionError("IFT Error: Bad Argument Type"), ["a","b"], 'ift')

    assertStackOp(["y"], None, [True,"y","n"], 'ifte')
    assertStackOp(["n"], None, [False,"y","n"], 'ifte')
    assertStackOp(["a", "y", "n"], AssertionError("IFTE Error: Bad Argument Type"), ["a","y","n"], 'ifte')

    assertStackOp([1,2,3], None, [1,2], 'push', 3)
    assertStackOp([1,2,2], None, [1,2], 'dup')
    assertStackOp([1,2,3,1], None, [1,2,3], 'pick', 3)
    assertStackOp([1,2,3,1], None, [1,2,3,3], 'pick')
    assertStackOp([1,3], None, [1,2,3], 'nip')
    assertStackOp([2,3], 1, [1,2,3], 'remove', 3)
    assertStackOp([1,2], 3, [1,2,3], 'pop')
    assertStackOp([1,2,3,3], None, [1,2,3], 'depth')
    assertStackOp([1,2,3], 3, [1,2,3], '_depth')
    assertStackOp([1,3,2], None, [1,2,3], 'swap')
    assertStackOp([1,2,3,2], None, [1,2,3], 'over')
    assertStackOp([1,2,3,2,3], None, [1,2,3], 'dup2')
    assertStackOp([1,2,3,3,3], None, [1,2,3], 'dupdup')
    assertStackOp([1,2], None, [1,2,3], 'drop')
    assertStackOp([1], None, [1,2,3], 'drop2')
    assertStackOp([1], None, [1,2,3,2], 'dropn')
    assertStackOp([1], None, [1,2,3], 'dropn', 2)

    assertStackOp([1,3,4,2], None, [1,2,3,4], 'roll', 3)
    assertStackOp([1,3,4,2], None, [1,2,3,4,3], 'roll')

    assertStackOp([1,4,2,3], None, [1,2,3,4], 'rolld', 3)
    assertStackOp([1,4,2,3], None, [1,2,3,4,3], 'rolld')

    assertStackOp([4,5,6], None, [1,2,3,4,5,6], 'keep', 3)
    assertStackOp([4,5], None, [1,2,3,4,5,2], 'keep')

    assertStackOp([1,3,4,2], None, [1,2,3,4], 'rot')
    assertStackOp([1,4,2,3], None, [1,2,3,4], 'rolld', 3)
    assertStackOp([1,4,2,3], None, [1,2,3,4], 'unrot')
    assertStackOp([1,2,3,4], 4, [1,2,3,4], 'value')
    assertStackOp([1,2,3,4], 2, [1,2,3,4], 'value', 3)
    assertStackOp([1,2,3,4,2,3,4], None, [1,2,3,4], 'dupn', 3)
    assertStackOp([1,2,3,4,9,9,9,3], None, [1,2,3,4], 'ndupn', 9, 3)
    assertStackOp([1,2,3,4,9,9,9,3], None, [1,2,3,4,9,3], 'ndupn')
    assertStackOp([4,3,2,1], None, [1,2,3,4], 'reverse_stack')
    assertStackOp([1,2,3,4,9], None, [1,2,3,4], 'insert', 1, 9)
    assertStackOp([1,9,2,3,4], None, [1,2,3,4], 'insert', 4, 9)
    assertStackOp([9,1,2,3,4], None, [1,2,3,4], 'insert', 5, 9)
    assertStackOp([1,2,3,4], False, [1,2,3,4], 'empty')
    assertStackOp([], True, [], 'empty')
    assertStackOp([], None, [1,2,3,4], 'clear')
    assertStackOp([9,2,3,4], None, [1,2,3,4], 'unpick', 4, 9)
    assertStackOp([[1,2,3]], None, [1,2,3,3], 'tolist')
    assertStackOp([[1,2,3]], None, [1,2,3], 'tolist', 3)
    assertStackOp([3], None, [[1,2,3]], 'get', 3)

    assertStackOp(['loremipsum'], None, ['lorem', 'ipsum'], 'concat')
    assertStackOp(['LOREM IPSUM'], None, ['lorem ipsum'], 'upper')
    assertStackOp(['lorem ipsum'], None, ['LOREM IPSUM'], 'lower')
    assertStackOp(['Lorem ipsum'], None, ['LOREM IPSUM'], 'capitalize')
    assertStackOp([11], None, ['LOREM IPSUM'], 'length')
    assertStackOp([True], None, ['LOREM IPSUM', 'LOREM'], 'startswith')
    assertStackOp([False], None, ['LOREM IPSUM', 'ABC'], 'startswith')
    assertStackOp([True], None, ['LOREM IPSUM', 'IPSUM'], 'endswith')
    assertStackOp([False], None, ['LOREM IPSUM', 'ABC'], 'endswith')
    assertStackOp(['L*REM IPSUM'], None, ['LOREM IPSUM', 'O', '*'], 'replace')
    assertStackOp(['lorem ipsum'], None, ['\t lorem ipsum  '], 'strip')
    assertStackOp(['lorem ipsum  '], None, ['\t lorem ipsum  '], 'lstrip')
    assertStackOp(['\t lorem ipsum'], None, ['\t lorem ipsum  '], 'rstrip')
    assertStackOp(['Lorem Ipsum'], None, ['lorem ipsum'], 'title')
    assertStackOp(['muspi merol'], None, ['lorem ipsum'], 'reverse')
    assertStackOp(['lorem'], None, ['loremipsum', 1, 5], 'substr')
    assertStackOp(['bob;dad'], None, ['{0};{1}', [ "bob", "dad" ]], 'format')

    assertStackOp([['lorem', 'ipsum', 'dolores', 'est']], None, ['lorem ipsum dolores est'], 'split')
    assertStackOp([['lorem', 'ipsum dolores est']], None, ['lorem ipsum dolores est'], 'split', ' ', 1)
    assertStackOp([['lorem', 'ipsum dolores est']], None, ['lorem ipsum dolores est', ' ', 1], 'split')

    assertStackOp([['lorem', 'ipsum', 'dolores', 'est']], None, ['lorem ipsum dolores est'], 'rsplit')
    assertStackOp([['lorem ipsum dolores', 'est']], None, ['lorem ipsum dolores est'], 'rsplit', ' ', 1)
    assertStackOp([['lorem ipsum dolores', 'est']], None, ['lorem ipsum dolores est', ' ', 1], 'rsplit')



    assertStackOp(([],{Variable('Q'): 88},[]), None,([88, Variable('Q')],{Variable('Q'): 44},[]), 'sto')

    assertStackOp(([44],{Variable('Q'): 44},[]), None,([Variable('Q')],{Variable('Q'): 44},[]), 'eval')

    assertStackOp([False], None, ["azerty"], 'isnum')
    assertStackOp([True], None, ["123"], 'isnum')
    assertStackOp([True], None, [1234], 'isnum')

    assertStackOp([True], None, ["azerty"], 'isstr')
    assertStackOp([True], None, ["123"], 'isstr')
    assertStackOp([False], None, [1234], 'isstr')

    assertStackOp(["azerty"], AssertionError("TONUM Error: Bad Argument Type"), ["azerty"], 'tonum')
    assertStackOp([123], None, ["123"], 'tonum')
    assertStackOp([1234], None, [1234], 'tonum')

    assertStackOp(["azerty"], None, ["azerty"], 'tostr')
    assertStackOp(["123"], None, ["123"], 'tostr')
    assertStackOp(["1234"], None, [1234], 'tostr')

    #assertStackOp([5,"6"], None, [5,6], 'tostr')
    #assertStackOp([5,"'A'"], None, [5,Variable("A")], 'tostr')
    #assertStackOp([5,6], None, [5,"6"], 'strto')
    #assertStackOp([5,"hello"], None, [5,"hello"], 'strto')
    #assertStackOp([5,Variable("v")], None, [5,"'v r'"], 'strto')
    #assertStackOp(['num'], None, [0], 'totype')
    #assertStackOp(['str'], None, ["azerty"], 'totype')

