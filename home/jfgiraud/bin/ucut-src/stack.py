#!/usr/bin/python3

from __future__ import division

import sys
import re
import sys


if sys.version_info >= (3, 0, 0):
    unicode = str

class Variable:
    def __init__(self, name):
        self.name = name
    #def __str__(self):
    #    return "'%s'" % self.name
    def __repr__(self):
        return "'%s'" % self.name
    def __eq__(self, other):
        return other.__class__ == Variable and self.name == other.name
    def __hash__(self):
        return hash(self.name)
    def apply(self, stack, **kwargs):
        if len(stack.l_variables) > 0 and self in stack.l_variables[-1]:
            stack.push(stack.l_variables[-1][self])
        elif self in stack.g_variables:
            stack.push(stack.g_variables[self])
        else: 
            stack.push(self)

class Function:
    def __init__(self, name, original):
        self.name = name
        self.original = original
    def apply(self, stack, **kwargs):
        f=getattr(stack, self.name)
        f()
    def __eq__(self, other):
        return other.__class__ == Function and self.original == other.original and self.name == other.name
    def __repr__(self):
        return "%s" % self.original

def in_quotes(states):
    for k in states:
        if states[k]:
            return True
    return False

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

def asnumber(token):
    if type(token) in [ int, float ]:
        return token
    elif re.match('^(-)?\\d+$', token):
        return int(token)
    elif re.match('^(-)?((\\d*\.)?\\d+?([eE][+-]?\\d+)?|nan|inf)$', token):
        return float(token)
    return None

class Reader:

    def __init__(self, input=[]):
        self.s = input[:]

    def read_until(self, tokens, until):
        if len(tokens) == 0:
            if until:
                if type(until) == list:
                    raise Exception('Unable to reach token "%s".' % '" or "'.join(until))
                else:
                    raise Exception('Unable to reach token "%s".' % until)
        token = tokens.pop(0)
        while token:
            if until and (token == until) or (type(until) == list and token in until) :
                return token
            if token == 'if':
                ifCmd = IfCmd()
                ifCmd.read_until(tokens, 'then')
                ifCmd.tocond()
                tok = ifCmd.read_until(tokens, ['else', 'end'])
                if tok == 'else':
                    ifCmd.totrue()
                    ifCmd.read_until(tokens, 'end')
                    ifCmd.tofalse()
                else:
                    ifCmd.totrue()
                self.s.append(ifCmd)
            elif token == 'case':
                caseCmd = CaseCmd()
                tok = caseCmd.read_until(tokens, ['then', 'end'])
                while tok is not None:
                    if tok == 'then':
                        caseCmd.tocond()
                        caseCmd.read_until(tokens, 'end')
                        caseCmd.totrue()
                        caseCmd.append()
                        tok = caseCmd.read_until(tokens, ['then', 'end'])
                    elif tok == 'end':
                        caseCmd.todefault()
                        break
                    else:
                        break
                self.s.append(caseCmd)
            elif token == 'start':
                startCmd = StartCmd()
                tok = startCmd.read_until(tokens, ['next', 'step'])
                if tok == 'next':
                    startCmd.tonext()
                else:
                    startCmd.tostep()
                self.s.append(startCmd)
            elif token == 'for':
                forCmd = ForCmd()
                tok = forCmd.read_until(tokens, ['next', 'step'])
                if tok == 'next':
                    forCmd.tonext()
                else:
                    forCmd.tostep()
                self.s.append(forCmd)
            elif token == 'while':
                whileCmd = WhileCmd()
                whileCmd.read_until(tokens, 'repeat')
                whileCmd.tocond()
                whileCmd.read_until(tokens, 'end')
                whileCmd.toloopst()
                self.s.append(whileCmd)
            elif token == 'do':
                doCmd = DoCmd()
                doCmd.read_until(tokens, 'until')
                doCmd.toloopst()
                doCmd.read_until(tokens, 'end')
                doCmd.tocond()
                self.s.append(doCmd)
            elif token == '->':
                localProg = LocalProgCmd()
                localProg.read_until(tokens, '{')
                localProg.tovars()
                localProg.read_until(tokens, '}')
                localProg.toprog()
                localProg.read_until(tokens, '}')
                localProg.toafter()
                tokens.insert(0, '}')
                self.s.append(localProg)
            elif token == '{':
                pCmd = Prog()
                pCmd.read_until(tokens, '}')
                self.s.append(pCmd)
            elif token in [ 'then', 'else', 'end', '}' ]:
                if type(until) == list:
                    raise Exception('Unable to reach token "%s".' % '" or "'.join(until))
                else:
                    raise Exception('Unable to reach token "%s".' % until)
            else:
                if re.match('^true$', token):
                    self.s.append(True)
                elif re.match('^false$', token):
                    self.s.append(False)
                elif re.match('^(-)?\\d+$', token):
                    self.s.append(int(token))
                elif re.match('^(-)?((\\d*\.)?\\d+?([eE][+-]?\\d+)?|nan|inf)$', token):
                    self.s.append(float(token))
                elif token in [ "depth", "drop", "drop2", "dropn", "dup", "dup2", "dupdup", "dupn", "ndupn", "nip", "over", "pick", "pick3", "roll", "rolld", "rot", "unrot", "keep", "pop", "push", "remove", "swap", "value", "insert", "empty", "clear", "unpick", "get", "upper", "lower", "capitalize", "length", "startswith", "endswith", "reverse", "replace", "concat", "strip", "lstrip", "rstrip", "title", "split", "rsplit", "ift", "ifte", '+', '-', '*', '/', '+', '==', '!=', '<', '>', '<=', '>=', 'eval', 'sto', 'and', 'or', 'not', 'xor', '?num', '->str', '?str', '->num', '->list', 'format', 'odd', 'even' ]:
                    
                    associations = {
                        '+': '_add',
                        '-': '_sub',
                        '*': '_mul',
                        '/': '_div',
                        '==': '_eq',
                        '!=': '_ne',
                        '<': '_lt',
                        '<=': '_le',
                        '>': '_gt',
                        '>=': '_ge',
                        'and': '_and',
                        'or': '_or',
                        'not': '_not',
                        'xor': '_xor',
                        '?num': 'isnum',
                        '?str': 'isstr',
                        '->num': 'tonum',
                        '->str': 'tostr',
                        '->list': 'tolist'
                    }

                    original = token

                    token = associations.get(token, original)

                    self.s.append(Function(token, original))
                elif token.startswith('"') and token.endswith('"'):
                    self.s.append(token[1:-1])
                elif token.startswith("'") and token.endswith("'"):
                    self.s.append(Variable(token[1:-1]))
                else:
                    self.s.append(Variable(token))
            if len(tokens) > 0:
                token = tokens.pop(0)
            else:
                if until:
                    if type(until) == list:
                        raise Exception('Unable to reach token "%s".' % '" or "'.join(until))
                    else:
                        raise Exception('Unable to reach token "%s".' % until)
                return None


def push_operations(stack, operations, executeProg=False, executeFunction=False):
    #print("---")
    for e in operations:
        #print '@@', e, stack, executeProg, executeFunction
        if type(e) in [ int, float, bool, str, unicode ]:
            stack.push(e)
        elif isinstance(e, Variable):
            if not executeFunction:
                stack.push(e)
            else:
                e.apply(stack)
        elif isinstance(e, Prog):
            if not executeProg:
                stack.push(e)
            else:
                push_operations(stack, e.s, False, True)
        elif isinstance(e, Command):
            e.apply(stack)
        elif isinstance(e, Function):
            if not executeFunction:
                stack.push(e)
            else:
                if e.original == 'eval':
                    if not stack.empty():
                        r = stack.pop()
                        #print(r, type(r), stack)
                        push_operations(stack, [ r ], True, True)
                else:
                    e.apply(stack)
        else:
            raise Exception('Unsupported type ', e)


class Prog(Reader):

    def __eq__(self, other):
        return other.__class__ == self.__class__ and self.s == other.s

    def __repr__(self):
        return 'PROG <' + str(self.s) + '>'

    def apply(self, stack, operations=None, **kwargs):
        
        executeProg = kwargs.get('executeProg', False)
        executeFunction = kwargs.get('executeFunction', False)

        if operations is None:
            operations = self.s
            
        push_operations(stack, operations, executeProg, executeFunction)


class Command(Reader):
    pass

class CaseCmd(Command):
    def __init__(self):
        Command.__init__(self)
        self.condition = []
        self.iftrue = []
        self.cases = []
        self.default = []
    def tocond(self):
        self.condition = self.s
        self.s = []
    def totrue(self):
        self.iftrue = self.s
        self.s = []
    def todefault(self):
        self.default = self.s
        self.s = []
    def append(self):
        self.cases.append( (self.condition, self.iftrue) )
        self.condition = []
        self.iftrue = []
        self.s = []
    def __repr__(self):
        return 'CASE <' + str(self.cases) + '> DEFAULT <' + str(self.default) + '>'
    def apply(self, stack):
        for (cond, iftrue) in self.cases:
            push_operations(stack, cond, False, True)
            #TODO check stack            
            r = stack.pop()
            if r:
                push_operations(stack, iftrue, False, True)
                break
        else:
            push_operations(stack, self.default, False, True)

class IfCmd(Command):
    def __init__(self, condition=[], iftrue=[], iffalse=[]):
        Command.__init__(self)
        self.condition = condition
        self.iftrue = iftrue
        self.iffalse = iffalse
    def tocond(self):
        self.condition = self.s
        self.s = []
    def totrue(self):
        self.iftrue = self.s
        self.s = []
    def tofalse(self):
        self.iffalse = self.s
        self.s = []
    def __repr__(self):
        return 'IF <' + str(self.condition) + '> THEN <' + str(self.iftrue) + '> ELSE <' + str(self.iffalse) + '>'
    def apply(self, stack):
        push_operations(stack, self.condition, False, True)
        #TODO check stack
        r = stack.pop()
        if r:
            push_operations(stack, self.iftrue, False, True)
        else:
            push_operations(stack, self.iffalse, False, True)

class StartCmd(Command):
    def __init__(self):
        Command.__init__(self)
        self.loopst = []
        self.next = False
        self.step = False
    def tonext(self):
        self.loopst = self.s
        self.next = True
        self.s = []
    def tostep(self):
        self.loopst = self.s
        self.step = True
        self.s = []
    def __repr__(self):
        if self.next:
            return 'START <' + str(self.loopst) + '> NEXT'
        else:
            return 'START <' + str(self.loopst) + '> STEP'
    def apply(self, stack):
        if self.next:
            stack._assert_enough_elements(2, 'start')
            stack._assert_number([1, 2], 'start')
            stop = stack.pop()
            start = stack.pop()
            i = start
            while i <= stop:
                push_operations(stack, self.loopst, False, True)
                i = i + 1
        elif self.step:
            stack._assert_enough_elements(2, 'start')
            stack._assert_number([1, 2], 'start')
            stop = stack.pop()
            start = stack.pop()
            i = start
            while i <= stop:
                push_operations(stack, self.loopst, False, True)
                stack._assert_enough_elements(1, 'start')
                stack._assert_number([1], 'start')
                i = i + stack.pop()
            

class ForCmd(Command):
    def __init__(self):
        Command.__init__(self)
        self.loopst = []
        self.next = False
        self.step = False
    def tonext(self):
        self.loopst = self.s
        self.next = True
        self.s = []
    def tostep(self):
        self.loopst = self.s
        self.step = True
        self.s = []
    def __repr__(self):
        if self.next:
            return 'FOR <' + str(self.loopst) + '> NEXT'
        else:
            return 'FOR <' + str(self.loopst) + '> STEP'
    def apply(self, stack):
        if self.next:
            stack._assert_enough_elements(2, 'for')
            stack._assert_number([1, 2], 'for') 
            stop = stack.pop()
            start = stack.pop()
            i = start
            while i <= stop:
                stack.push(i)
                stack._set_local_vars([self.loopst[0]], 'for')
                push_operations(stack, self.loopst[1:], False, True)
                stack._restore_vars()
                i = i + 1
        elif self.step:
            stack._assert_enough_elements(2, 'for')
            stack._assert_number([1, 2], 'for') 
            stop = stack.pop()
            start = stack.pop()
            i = start
            while i <= stop:
                stack.push(i)
                stack._set_local_vars([self.loopst[0]], 'for')
                push_operations(stack, self.loopst[1:], False, True)
                stack._restore_vars()
                stack._assert_enough_elements(1, 'for')
                stack._assert_number([1], 'for')
                i = i + stack.pop()


class LocalProgCmd(Command):
    def __init__(self):
        Command.__init__(self)
        self.vars = []
    def tovars(self):
        self.vars = self.s
        self.vars.reverse()
        self.s = []
    def toprog(self):
        self.prog = self.s
        self.s = []
    def toafter(self):
        self.after = self.s
        self.s = []
    def apply(self, stack):
        stack._set_local_vars(self.vars, '->')
        push_operations(stack, self.prog, False, True)
        stack._restore_vars()
        push_operations(stack, self.after, False, True)
    def __repr__(self):
        return '{ -> ' + str(self.vars) + ' { ' + str(self.prog) + ' } ' + str(self.after) + ' }'


class WhileCmd(Command):
    def __init__(self):
        Command.__init__(self)
        self.loopst = []
        self.condition = []
    def tocond(self):
        self.condition = self.s
        self.s = []
    def toloopst(self):
        self.loopst = self.s
        self.s = []
    def __repr__(self):
        return 'WHILE <' + str(self.condition) + '> REPEAT <' + str(self.loopst) + '> END'
    def apply(self, stack):
        push_operations(stack, self.condition, False, True)
        # TODO check stack
        r = stack.pop()
        while r:
            push_operations(stack, self.loopst, False, True)
            push_operations(stack, self.condition, False, True)
            r = stack.pop()

class DoCmd(Command):
    def __init__(self):
        Command.__init__(self)
        self.loopst = []
        self.condition = []
    def tocond(self):
        self.condition = self.s
        self.s = []
    def toloopst(self):
        self.loopst = self.s
        self.s = []
    def __repr__(self):
        return 'DO <' + str(self.loopst) + '> UNTIL <' + str(self.condition) + '> END'
    def apply(self, stack):
        r = 1
        while r:
            push_operations(stack, self.loopst, False, True)
            push_operations(stack, self.condition, False, True)
            # TODO check stack
            r = stack.pop()


class Stack:

    def __init__(self, elements=[]):
        self.elements = elements
        self.g_variables = {}
        self.l_variables = []

    def sto(self):
        self._assert_enough_elements(2, 'sto')
        self.__assert_identifier([1], 'sto')
        identifier = self.pop()
        self.g_variables[identifier] = self.pop()

    def eval(self):
        x = self.pop()
        if type(x) in [ str, unicode ]:
            self.push(x)
        elif type(x) in [ int, float ]:
            self.push(x)
        else:
            x.apply(self, executeProg=False, executeFunction=True)

    def _set_local_vars(self, variables, caller):
        self._assert_enough_elements(len(variables), caller)
        if len(self.l_variables) == 0:
            v = {}
        else:
            v = self.l_variables[-1].copy()
        for e in variables:
            v[e] = self.pop()
        self.l_variables.append(v)

    def _restore_vars(self):
        self.l_variables.pop()

    
    def _depth(self):
        return len(self.elements)

    def depth(self):
        '''Return the number of objects on the stack'''
        self.push(len(self.elements))
    def drop(self):
        '''Removes the object in level 1'''
        self._assert_enough_elements(1, 'drop')
        self.dropn(1)
    def drop2(self):
        '''Removes the objects in levels 1 and 2'''
        self._assert_enough_elements(2, 'drop2')
        self.dropn(2)
    def dropn(self,n=None):
        '''Removes the first n+1 objects from the stack (n in level 1)'''
        n = self.__getn(n, 'dropn')
        self._assert_enough_elements(n, 'dropn')
        for i in range(0, n):
            self.pop()
    def dup(self):
        '''Duplicates the object in level 1'''
        self.__assert_not_empty('dup')
        self.pick(1)
    def dup2(self):
        '''Duplicates the objects in level 1 and 2'''
        self._assert_enough_elements(2, 'dup2')
        self.over()
        self.over()
    def dupdup(self):
        '''Duplicates the object in level 1 twice'''
        self._assert_enough_elements(1, 'dupdup')
        self.pick(1)
        self.pick(1)
    def dupn(self, n=None):
        '''Duplicates n objects on the stack, starting at level 2 (n is in level 1)'''
        n = self.__getn(n, 'dupn')
        if n > 0:
            self._assert_enough_elements(n, 'dupn')
            for i in range(0, n):
                self.pick(n)
    def ndupn(self, *args):
        '''Duplicates n times the object on level 2 (n is in level 1), 
        and leaves n in level 1'''
        if len(args) == 0:
            self.__assert_int([1], 'ndupn')
            n = self.pop()
            e = self.pop()
        elif len(args) == 2:
            (e, n) = args
        else:
            raise Exception("NDUPN: Invalid call.")
        self.__assert_int(n, 'ndupn')
        for i in range(0, n):
            self.push(e)
        self.push(n)
    def nip(self):
        '''Drops the second object of the stack'''
        self._assert_enough_elements(2, 'nip')
        self.remove(2)
    def over(self):
        '''Returns a copy of the object in level 2'''
        self._assert_enough_elements(2, 'over')
        self.pick(2)
    def pick(self, n=None):
        '''Returns a copy of the object in level n+1 to level 1 (n is in level 1)'''
        n = self.__getn(n, 'dupn')
        if n > 0:
            self._assert_enough_elements(n, 'pick')
            self.push(self.value(n))
    def pick3(self):
        '''Returns a copy of the object in level 3 to level 1'''
        self.pick(3)

    def roll(self, n=None):
        '''Moves the contents of the level n+1 to level 1, and rolls upwards 
        the portion of the stack beneath the specified level  (n is in level 1)'''
        n = self.__getn(n, 'roll')
        self._assert_enough_elements(n, 'roll')
        e = self.remove(n)
        self.push(e)
    def rolld(self, n=None):
        '''Rolls down a portion of the stack between level 2 and level n+1 
        (n is in level 1)'''
        n = self.__getn(n, 'rolld')
        self._assert_enough_elements(n, 'rolld')
        e = self.pop()
        self.insert(n, e)
    def rot(self):
        '''Rotates the first three objects on the stack, 
        moving the object on level 3 to level 1 (equivalent to 3 ROLL)'''
        self._assert_enough_elements(3, 'rot')
        self.roll(3)
    def unrot(self):
        '''Changes the order of the first three objects on the stack.
        The order of the change is the opposite to that of the ROT command'''
        self._assert_enough_elements(3, 'unrot')
        self.rolld(3)

    def keep(self, n=None):
        '''Clears all levels above the level n+1 (n is in level 1)'''
        n = self.__getn(n, 'keep')
        self._assert_enough_elements(n, 'keep')
        self.elements = self.elements[-n:]

    def pop(self):
        '''Removes the object in level 1 and returns it'''
        self.__assert_not_empty('pop')
        return self.remove(1)

    def push(self, o):
        '''Pushes the given object onto the top of the stack'''
        self.elements.append(o)

    def remove(self, i=1):
        self._assert_enough_elements(i, 'remove')
        r = self.elements[self._depth()-i]
        del self.elements[self._depth()-i]
        return r

    def swap(self):
        '''Swaps objects in levels 1 and 2'''
        self._assert_enough_elements(2, 'swap')
        l = self.pop()
        b = self.pop()
        self.push(l)
        self.push(b)

    def value(self, i=1):
        '''Returns the object in level n without removing it'''
        self._assert_enough_elements(i, 'value')
        return self.elements[self._depth()-i]

    def reverse_stack(self):
        self.elements.reverse()

    def insert(self, i, e):
        ####### i
        self._assert_enough_elements(i-1, 'insert')
        self.elements.insert(self._depth()-i+1, e)

    def empty(self):
        return self._depth() == 0

    def clear(self):
        '''Remove all object on the stack'''
        del self.elements[:]

    def unpick(self, i, e):
        ####### i
        if i > 0:
            self._assert_enough_elements(i, 'unpick')
            self.elements[self._depth()-i]=e
    def __eq__(self, s):
        return s.__class__ == Stack and self.elements == s.elements

    def tolist(self, i=None):
        if i is None:
            self.__assert_not_empty('tolist')
            i = self.pop()
        self._assert_enough_elements(i, 'tolist')
        result = []
        while i > 0: 
            result.insert(0, self.pop())
            i=i-1
        self.push(result)
    def get(self, i):
        o = self.pop()
        if type(o) != list:
            raise Exception("GET: Bad argument type.")
        l = o
        if i < 1 or i > len(l):
            raise Exception("GET: Bad argument value.")
        self.push(l[i-1])
    def __repr__(self):
        s = ''
        for i in range(0, len(self.elements)):
            s += '%s\t%s\n' % (i, self.value(i+1))
        return s
    def upper(self):
        self.__assert_string([1], 'upper')
        self.push(self.pop().upper())
    def lower(self):
        self.__assert_string([1], 'lower')
        self.push(self.pop().lower())
    def capitalize(self):
        self.__assert_string([1], 'capitalize')
        self.push(self.pop().capitalize())
    def length(self):
        #### renommer en size
        # head 
        # tail
        self.__assert_string([1], 'length')
        self.push(len(self.pop()))
    def startswith(self):
        self.__assert_string([1, 2], 'startswith')
        pref = self.pop()
        text = self.pop()
        self.__push_as_bool(text.startswith(pref))
    def endswith(self):
        self.__assert_string([1, 2], 'endswith')
        pref = self.pop()
        text = self.pop()
        self.__push_as_bool(text.endswith(pref))
    def format(self):
        self.__assert_string([2], 'format')
        args = self.pop()
        fmt = self.pop()
        self.push(fmt.format(*args))
    def concat(self):
        self.__assert_string([1,2], 'concat')
        b = self.pop()
        a = self.pop()
        self.push(a+b)
    def reverse(self):
        self.__assert_string([1], 'reverse')
        text = self.pop()
        self.push(text[::-1])
    def substr(self):
        self.__assert_string([3], 'substr')
        self.__assert_int([1,2], 'substr')
        toindex = self.pop()
        fromindex = self.pop()
        text = self.pop()
        self.push(text[fromindex-1:toindex])
    def replace(self):
        self.__assert_string([1, 2, 3], 'replace')
        by = self.pop()
        what = self.pop()
        text = self.pop()
        #print(by, what, text)
        self.push(text.replace(what, by))
    def strip(self):
        self.__assert_string([1], 'strip')
        self.push(self.pop().strip())
    def lstrip(self):
        self.__assert_string([1], 'lstrip')
        self.push(self.pop().lstrip())
    def rstrip(self):
        self.__assert_string([1], 'rstrip')
        self.push(self.pop().rstrip())
    def title(self):
        self.__assert_string([1], 'title')
        self.push(self.pop().title())
    def split(self, *args):
        if len(args) == 2:
            (sep, maxsplit) = args
        elif len(args) != 0:
            raise Exception('SPLIT: Invalid call.')
        else:
            if type(self.value()) in [ int ]:
                self.__assert_int([1], 'split')
                self.__assert_string([2], 'split', True)
                self.__assert_string([3], 'split')
                maxsplit = self.pop()
                sep = self.pop()
            else:
                maxsplit = -1
                sep = None
                self.__assert_string([1], 'split')
        text = self.pop()
        self.push(text.split(sep, maxsplit))
    def rsplit(self, *args):
        if len(args) == 2:
            (sep, maxsplit) = args
        elif len(args) != 0:
            raise Exception('RSPLIT: Invalid call.')
        else:
            if type(self.value()) in [ int ]:
                self.__assert_int([1], 'rsplit')
                self.__assert_string([2], 'rsplit', True)
                self.__assert_string([3], 'rsplit')
                maxsplit = self.pop()
                sep = self.pop()
            else:
                maxsplit = -1
                sep = None
                self.__assert_string([1], 'rsplit')
        text = self.pop()
        self.push(text.rsplit(sep, maxsplit))
    def _add(self):
        self._assert_number([1, 2], 'add')
        self.push(self.pop()+self.pop())
    def _sub(self):
        self._assert_number([1, 2], 'sub')
        self.swap()
        self.push(self.pop()-self.pop())
    def odd(self):
        self.__assert_int([1], 'odd')
        self.__push_as_bool(self.pop() % 2 == 1)
    def even(self):
        self.__assert_int([1], 'even')
        self.__push_as_bool(self.pop() % 2 == 0)
    def _mul(self):
        self._assert_number([1, 2], 'mul')
        self.push(self.pop()*self.pop())
    def _div(self):
        self._assert_number([1, 2], 'div')
        self.swap()
        self.push(self.pop()/self.pop())
    def _eq(self):
        self._assert_enough_elements(2, '==')
        self.__push_as_bool(self.pop() == self.pop())
    def _ne(self):
        self._assert_enough_elements(2, '!=')
        self.__push_as_bool(self.pop() != self.pop())
    def _lt(self):
        self._assert_enough_elements(2, '<')
        self.swap()
        self.__push_as_bool(self.pop() < self.pop())
    def _le(self):
        self._assert_enough_elements(2, '<=')
        self.swap()
        self.__push_as_bool(self.pop() <= self.pop())
    def _gt(self):
        self._assert_enough_elements(2, '>')
        self.swap()
        self.__push_as_bool(self.pop() > self.pop())
    def _ge(self):
        self._assert_enough_elements(2, '>=')
        self.swap()
        self.__push_as_bool(self.pop() >= self.pop())
    def _and(self):
        self.__assert_bool([1, 2], 'and')
        (x, y) = (self.__pop_as_bool(), self.__pop_as_bool())
        self.__push_as_bool(x and y)
    def _or(self):
        self.__assert_bool([1, 2], 'or')
        (x, y) = (self.__pop_as_bool(), self.__pop_as_bool())
        self.__push_as_bool(x or y)
    def _xor(self):
        self.__assert_bool([1, 2], 'xor')
        (x, y) = (self.__pop_as_bool(), self.__pop_as_bool())
        self.__push_as_bool(x ^ y)
    def _not(self):
        self.__assert_bool([1], 'not')
        x = self.__pop_as_bool()
        self.__push_as_bool(not x)
    def tostr(self):
        self._assert_enough_elements(1, '->str')
        x = self.pop()
        self.push(str(x))
    # def totype(self):
    #     self._assert_enough_elements(1, 'type')
    #     x = self.pop()
    #     if type(x) in [ int, long, float ]:
    #         self.push('num')
    #     elif type(x) in [ str, unicode ]:
    #         self.push('str')
    #     else:
    #         self.push('?')
    # def strto(self):
    #     self._assert_enough_elements(1, 'str->')
    #     x = self.pop()
    #     reader = Reader([])
    #     reader.read_until([ x ], None)
    #     push_operations(self, reader.s, False, False)
    def ift(self):
        self._assert_enough_elements(2, 'ift')
        self.__assert_bool([2], 'ift')
        self.swap()
        if self.pop():
            self.eval()
        else:
            self.drop()

    def ifte(self):
        self._assert_enough_elements(3, 'ifte')
        self.__assert_bool([3], 'ifte')
        self.rot()
        if self.pop():
            self.drop()
            self.eval()
        else:
            self.nip()
            self.eval()

    def isnum(self):
        self._assert_enough_elements(1, '?num')
        r = self.pop()
        if type(r) in [ int, float ]:
            self.__push_as_bool(True)
        elif asnumber(r) is not None:
            self.__push_as_bool(True)
        else:
            self.__push_as_bool(False)

    def tonum(self):
        self._assert_enough_elements(1, '->num')
        self.dup()
        self.isnum()
        r = self.pop()
        if r:
            self.push(asnumber(self.pop()))
        else:
            self.__assert_int([1], 'tonum')

    def isstr(self):
        self._assert_enough_elements(1, '?str')
        r = self.pop()
        self.__push_as_bool(type(r) in [ str, unicode ])

    def __push_as_bool(self, b):
        if b:
            self.push(True)
        else:
            self.push(False)

    def __pop_as_bool(self):
        if self.pop():
            return True
        else:
            return False


    def __getn(self, n, caller):
        if n is None:
            self.__assert_int([1], caller)
            n = self.pop()
        
        return n
    
    def __assert_identifier(self, i, caller):
        if type(i) == list:
           m=max(i)
           self._assert_enough_elements(m, caller)
           for i in i[:]:
               assert isinstance(self.value(i), Variable), "%s Error: Bad Argument Type" % caller.upper()
        else:
            self._assert_enough_elements(i, caller)
            assert isinstance(i, Variable), "%s Error: Bad Argument Type" % caller.upper()
        
    def __assert_bool(self, i, caller, noneTypeAllowed=False):
        types = [ type(True) ]
        if noneTypeAllowed:
            types.append(type(None))
        if type(i) == list:
            m=max(i)
            self._assert_enough_elements(m, caller)
            for i in i[:]:
                assert type(self.value(i)) in types, "%s Error: Bad Argument Type" % caller.upper()
        else:
            self._assert_enough_elements(i, caller)
            assert type(i) in types, "%s Error: Bad Argument Type" % caller.upper()

    def __assert_string(self, i, caller, noneTypeAllowed=False):
        types = [ str, unicode ]
        if noneTypeAllowed:
            types.append(type(None))
        if type(i) == list:
            m=max(i)
            self._assert_enough_elements(m, caller)
            for i in i[:]:
                assert type(self.value(i)) in types, "%s Error: Bad Argument Type" % caller.upper()
        else:
            self._assert_enough_elements(i, caller)
            assert type(i) in types, "%s Error: Bad Argument Type" % caller.upper()
            
    def __assert_int(self, i, caller, noneTypeAllowed=False):
        types = [ int ]
        if noneTypeAllowed:
            types.append(type(None))
        if type(i) == list:
           m=max(i)
           self._assert_enough_elements(m, caller)
           for i in i[:]:
               assert type(self.value(i)) in types, "%s Error: Bad Argument Type" % caller.upper()
        else:
            self._assert_enough_elements(i, caller)
            assert type(i) in types, "%s Error: Bad Argument Type" % caller.upper()
    
    def _push_variables(self, variables):
        self.variables.append(variables)

    def _assert_number(self, i, caller, noneTypeAllowed=False):
        types = [ int, float ]
        if noneTypeAllowed:
            types.append(type(None))
        if type(i) == list:
           m=max(i)
           self._assert_enough_elements(m, caller)
           for i in i[:]:
                assert type(self.value(i)) in types, "%s Error: Bad Argument Type" % caller.upper()
        else:
            self._assert_enough_elements(i, caller)
            assert type(i) in types, "%s Error: Bad Argument Type" % caller.upper()
    def __assert_not_empty(self, caller):
        assert not self.empty(), "%s Error: Empty stack." % caller.upper()
    def _assert_enough_elements(self, i, caller):
        assert type(i) == int and i >= 0, "%s: Invalid Value" % caller.upper()
        assert i <= self._depth(), "%s Error: Too Few Arguments" % caller.upper()


