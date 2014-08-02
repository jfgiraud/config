#!/usr/bin/python3

from stack import *

if __name__ == '__main__':

    def assertTokenize(expected, pattern):
        tokens = tokenize(pattern)
        assert expected == tokens, "EXPECTED: %s ACTUAL: %s" % (str(expected), str(tokens))

    def assertStackOp(expected, elements, ops, **kwargs):
        tokens = tokenize(ops)
        if True:
            print('*' * 80)
            print(expected, elements, ops)
            print(tokens)
            print('-' * 80)


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



        i=Stack(elements)
        e=Stack(expected)
        i.g_variables = igv
        i.l_variables = ilv

        try:
            p = Prog()
            p.read_until(tokens, None)
            if False:
                print(p.s)
            p.apply(i, executeFunction=True)
            assert e == i, "EXPECTED: %s ACTUAL: %s" % (str(e), str(i))
            if kwargs.get('check_gv', True):
                assert egv == i.g_variables, "GV"
            if kwargs.get('check_lv', True):
                assert elv == i.l_variables, "LV"
        except AssertionError as e:
            ret = kwargs.get('ret', None)
            if ret is not None:
                assert ret.args[0] == e.args[0], e.args[0]
            else:
                raise e

            
    assertTokenize(['abc', 'def'], "abc def") 
    assertTokenize(['"abc def"'], "\"abc def\"") 
    assertTokenize(['"abc"'], '"abc"') 
    assertTokenize(['"a"bc"'], '"a\\"bc"') 
    #assertTokenize(['ee"'], 'ee"') 
    #assertTokenize(['ee"'], 'ee\"') 
    assertTokenize(['ee"ff'], 'ee\\"ff') 
    assertTokenize(['"""', '"*"', 'replace'], '"\\"" "*" replace') 
    assertTokenize(['"\\"', '"*"', 'replace' ], '"\\\\" "*" replace')    

    if 1:
        assertStackOp([3], [3], '')
        assertStackOp([3, 1], [3], '1')
        assertStackOp([3, 7], [3], '7')
        assertStackOp([3, Prog([2, 5])], [3], '{ 2 5 }')
        assertStackOp([3, Prog([2, 'abc', 5])], [3], '{ 2 "abc" 5 }')
        assertStackOp([4], [3], '1 +') 
        assertStackOp([3, 1, 2], [3], '1 2')
        assertStackOp([3, 1, 'hello'], [3], '1 "hello"')
        assertStackOp([3, 1, 'hello'], [3], '1 "hello" eval')
        assertStackOp([3, 1], [3], '1 eval')
        assertStackOp([3, Prog([2, 5, Function('_add', '+')])], [3], '{ 2 5 + }')
        assertStackOp([3, 7], [3], '{ 2 5 + } eval')
        assertStackOp([3, Prog([5, 'abc', 5]), 7], [3], '{ { 5 "abc" 5 } 2 5 + } eval')

        assertStackOp([1, Prog([2, 3, Function('_add', '+')]), 1], [], '{ 1 { 2 3 + } 1 } eval')

        assertStackOp([2, Prog([1, Function('eval', 'eval')])], [2], '{ 1 eval }')
        assertStackOp([Prog([Prog([2, 3, Function('_add', '+')]), Function('eval', 'eval'), 1, Function('_add', '+')])], [], '{ { 2 3 + } eval 1 + }')
        assertStackOp([6], [], '{ { 2 3 + } eval 1 + } eval')

        ### ift
        assertStackOp(["y"], [3], '3 == "y" ift') 
        assertStackOp([], [3], '5 == "y" ift') 
        assertStackOp([11], [10, 3], '3 == { 1 + } ift') 
        assertStackOp([10], [10, 3], '5 == { 1 + } ift') 
        assertStackOp([8], [5], 'true { 3 + } ift')
        assertStackOp([8], [5, True], '{ 3 + } ift')
        
        ### ifte
        assertStackOp(["y"], [3], '3 == "y" "n" ifte') 
        assertStackOp(["n"], [3], '5 == "y" "n" ifte') 
        assertStackOp([11], [10, 3], '3 == { 1 + } { 1 - } ifte') 
        assertStackOp([9], [10, 3], '5 == { 1 + } { 1 - } ifte') 
        assertStackOp([4], [], '{ "abc" true { length 1 + } { length 1 - } ifte } eval') 
        assertStackOp([2], [], '{ "abc" false { length 1 + } { length 1 - } ifte } eval') 
        
        ### if/then/end
        assertStackOp([], [3], '{ if 5 > then 1 end } eval')
        assertStackOp([], [3], 'if 5 > then 1 end')
        assertStackOp([33], [3], 'if 5 > then 1 end 33')
        assertStackOp([1], [6], 'if 5 > then 1 end eval')
        assertStackOp([1], [6], '{ if 5 > then 1 end } eval')

        ### if/then/else/end
        assertStackOp([0], [3], '{ if 5 > then 1 else 0 end } eval') 
        assertStackOp([101], [100, 3], '{ if 5 <= then 1 + else 1 - end } eval') 
        assertStackOp([0], [3], 'if 5 > then 1 else 0 end eval')

        ### case
        assertStackOp(["eq"], [5], 'case dup 5 == then "eq" end dup 5 < then "less" end dup 5 > then "more" end end eval swap drop') 
        assertStackOp(["more"], [6], 'case dup 5 == then "eq" end dup 5 < then "less" end dup 5 > then "more" end end eval swap drop') 
        assertStackOp(["less"], [4], 'case dup 5 == then "eq" end dup 5 < then "less" end dup 5 > then "more" end end eval swap drop') 
        assertStackOp(["eq"], [5], 'case dup 5 == then "eq" end dup 5 < then "less" end dup 5 > then "more" end end eval swap drop') 
        assertStackOp(["more"], [6], 'case dup 5 == then "eq" end dup 5 < then "less" end dup 5 > then "more" end end eval swap drop') 
        assertStackOp(["found"], [1], '{ case dup 1 == then "found" end "not found" end swap drop } eval') 
        assertStackOp(["not found"], [4], '{ case dup 1 == then "found" end "not found" end swap drop } eval') 

        ### start / end
        assertStackOp(["hello", "hello", "hello"], [], '{ 0 1 + 3 start "hello" next } eval', ret=AssertionError("START Error: Too Few Arguments")) 
        assertStackOp(["hello", "hello", "hello"], [], '{ 0 1 + "a" start "hello" next } eval', ret=AssertionError("START Error: Bad Argument Type")) 
        assertStackOp(["hello", "hello", "hello"], [], '{ 1 3 start "hello" next } eval')
        assertStackOp(["hello", "hello", "hello"], [], '1 3 start "hello" next eval')
        assertStackOp(["hello", "hello"], [], '{ 1.5 3 start "hello" next } eval')
        assertStackOp([5], [], '0 { 1 5 start 1 + next } eval')
        assertStackOp([5], [], '0 1 5 start 1 + next')
        assertStackOp([5, 555], [], '0 1 5 start 1 + next 555')

        ### start / step
        assertStackOp(["hello", "hello", "hello"], [], '{ 1 5 start "hello" 2 step } eval')
        assertStackOp([7], [], '{ 1 1 5 start 2 + 2 step } eval')


        ## tester 4 d sto '{ -> d { d 2 * } d 1 + } eval'
        ## attention, si surchage de dup, l'appel est la variable pas la methode!
        assertStackOp([5], [8], '{ -> d { 3 2 + } } eval')
        assertStackOp([16], [8], '{ -> d { d 2 * } } eval')
        assertStackOp(([16,67],{Variable('a'): 66},[]), ([8],{Variable('a'): 66},[]), '{ -> d { d 2 * } a 1 + } eval')
        assertStackOp(([16,68],{Variable('d'): 66},[]), ([8],{Variable('d'): 66},[]), '{ -> d { d 2 * } 2 d + } eval')
        assertStackOp([16,3], [8], '{ -> d { d 2 * } 2 1 + } eval')
        assertStackOp([13], [2, 3], '{ -> a b { a 2 * b 3 * + } } eval')

        assertStackOp([48], [8], '{ -> d { d 2 * { -> d { d 3 * } } eval } } eval')
        assertStackOp([45], [], '0 1 5 for a a { -> b { b 2 * } } eval a + + next')
        assertStackOp([45], [], '0 1 5 for a a dup { -> b { b 2 * + } } eval + next')
        assertStackOp([1, 3, 5], [], '1 5 for a a 2 step')
        
        # while
        assertStackOp([5, 4, 3, 2, 1, 0], [], '5 while dup 0 > repeat dup 1 - end')


    assertStackOp([15, 16, 17, 18], [], '5 do dup 10 + swap 1 + until dup 8 <= end drop')

    assertStackOp([66], [], '33 { -> d { d 2 * } } eval')
    assertStackOp([66], [], '{ -> d { d 2 * } } q sto 33 q eval', check_gv=False)

    assertStackOp(["a;b"], [], '"{0};{1}" "a" "b" 2 ->list format')

    assertStackOp(["b\\*c"], ['b\\ac'], '"a" "*" replace')
    assertStackOp(["b*c"], ['b\\ac'], '"\\\\a" "*" replace')
    assertStackOp(["b*c"], ['b\ac'], '"\a" "*" replace')
    assertStackOp(["b*c"], ['b"c'], '"\\"" "*" replace')
    assertStackOp(["b*ac"], ['b\\ac'], '"\\\\" "*" replace')


    sys.exit(0)

    # 8 d sto { -> d { d 3 + { -> d { 100 d * } d } eval d } eval d eval } 
    # 1 donne 400 
        



