#!/usr/bin/python
# coding: utf

import readline
import sys
import tpg
import itertools

def make_op(s):
    return {
        '+': lambda x,y: x+y,
        '-': lambda x,y: x-y,
        '*': lambda x,y: x*y,
        '/': lambda x,y: x/y,
        '&': lambda x,y: x&y,
        '|': lambda x,y: x|y,
    }[s]

class Vector(list):
    def __init__(self, *argp, **argn):
        list.__init__(self, *argp, **argn)

    def __str__(self):
        rows, cols = self.dim()
        if cols == 0:
            return "[" + " ".join(str(c) for c in self) + "]"
        else:
            paddings = []
            for c in range(cols):
                paddings.append('{:^' + str(max(map(lambda i: len(str(i)), [self[r][c] for r in range(rows)]))) + '}')

            result = ''
            for r in range(rows):
                result += '|'
                for c in range(cols):
                    result += paddings[c].format(self[r][c])
                    if c < cols-1:
                        result += ' '
                result += '|\n'
            return result

    def __op(self, a, op):
        try:
            return self.__class__(op(s,e) for s,e in zip(self, a))
        except TypeError:
            return self.__class__(op(c,a) for c in self)

    def __add__(self, a): return self.__op(a, lambda c,d: c+d)
    def __sub__(self, a): return self.__op(a, lambda c,d: c-d)
    def __div__(self, a): return self.__op(a, lambda c,d: c/d)
    def __mul__(self, b):
        if isinstance(b, Vector):
            a = self
            da_rows, da_cols = a.dim()
            db_rows, db_cols = b.dim()
            if da_cols == 0:    # это вектор
                if da_cols != db_cols:
                    raise tpg.Error('cannot multiply vector with different sizes')
                # скалярно делаем произведение
                return reduce(lambda v, n: v + n[0]*n[1], zip(self, b), 0)
            else:      # матрица
                if da_cols != db_rows:
                    raise tpg.Error('cannot multiply matrices')
                result = Vector()
                for r in range(da_rows):
                    row = Vector()
                    for c in range(db_cols):
                        value = 0
                        for n in range(db_rows):
                            value += a[r][n] * b[n][c]
                        row.append(value)
                    result.append(row)
                return result
        return self.__op(b, lambda c,d: c*d)

    def __and__(self, a):
        try:
            return reduce(lambda s, (c,d): s+c*d, zip(self, a), 0)
        except TypeError:
            return self.__class__(c and a for c in self)

    def __or__(self, a):
        try:
            return self.__class__(itertools.chain(self, a))
        except TypeError:
            return self.__class__(c or a for c in self)

    def dim(self):
        """
        Размер матрицы
        Возвращает количество строк и количество столбцов
        Если это вектор, то количество столбцов - 0
        """
        rows = len(self)
        if rows == 0:
            return 0, 0

        cols = Vector.safe_len(self[0])
        for row in self:
            if Vector.safe_len(row) != cols:
                return rows, 0
        return rows, cols

    @staticmethod
    def safe_len(obj):
        if hasattr(obj, '__len__'):
            return len(obj)
        else:
            return 0

class Calc(tpg.Parser):
    r"""

    separator spaces: '\s+' ;
    separator comment: '#.*' ;

    token fnumber: '\d+[.]\d*' float ;
    token number: '\d+' int ;
    token op1: '[|&+-]' make_op ;
    token op2: '[*/]' make_op ;
    token id: '\w+' ;

    START/e -> Operator $e=None$ | Expr/e | $e=None$ ;
    Operator -> Assign ;
    Assign -> id/i '=' Expr/e $Vars[i]=e$ ;
    Expr/t -> Fact/t ( op1/op Fact/f $t=op(t,f)$ )* ;
    Fact/f -> Atom/f ( op2/op Atom/a $f=op(f,a)$ )* ;
    Atom/a ->   Vector/a
              | id/i ( check $i in Vars$ | error $"Undefined variable '{}'".format(i)$ ) $a=Vars[i]$
              | fnumber/a
              | number/a
              | '\(' Expr/a '\)' ;
    Vector/$Vector(a)$ -> '\[' '\]' $a=[]$ | '\[' Atoms/a '\]' ;
    Atoms/v -> Atom/a Atoms/t $v=[a]+t$ | Atom/a $v=[a]$ ;

    """

if __name__ == '__main__':
    calc = Calc()
    Vars={}
    PS1='--> '

    Stop=False
    while not Stop:
        res = None
        try:
            line = raw_input(PS1)
            res = calc(line)
        except tpg.Error as exc:
            print >> sys.stderr, exc
            res = None
        except KeyboardInterrupt:
            print "exited"
            break
        if res is not None:
            print res
