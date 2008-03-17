#coding=gbk
from ply import yacc

from interpretor.kernelc.lex import *
from interpretor.kernelc.ast import Node

start = 'prog'

def p_prog(p):
    '''prog : prog fdef
            | fdef
    '''
    p[0] = Node("prog", p[1:])

def p_fdef(p):
    "fdef : kw_func id '{' stlist '}'"
    p[0] = Node("fdef", p[1:])
    p.parser.functions[p[2]] = p[4] #函数名对应的函数体

def p_stlist(p):
    '''stlist : st ';' stlist
              | st
    '''
    p[0] = Node("stlist", p[1:])

def p_st(p):
    '''st : exp
          | cond
          | loop
          | print_st
          | println_st
    '''
    p[0] = Node("st",p[1:])

def p_print_st(p):
    ''' print_st : io_print '(' exp ')'
                 | io_print '(' ')'
    '''
    p[0] = Node("print_st",p[1:])

def p_println_st(p):
    ''' println_st : io_println '(' exp ')'
                   | io_println '(' ')'
    '''
    p[0] = Node("println_st",p[1:])


def p_cond(p):
    '''cond : kw_if '(' exp ')' st
            | kw_if '(' exp ')' st  kw_else st
    '''
    p[0] = Node("cond",p[1:])

def p_loop(p):
    '''loop : kw_while '(' exp ')'
            | kw_while '(' exp ')' st
    '''
    p[0] = Node("loop",p[1:])

def p_exp(p):
    '''exp : orexp
           | orexp '=' orexp
    '''
    p[0] = Node("exp",p[1:])


def p_orexp(p):
    '''orexp : andexp
             | andexp orop orexp
    '''
    p[0] = Node("orexp",p[1:])

def p_andexp(p):
    '''andexp : relexp
              | relexp andop andexp
    '''
    p[0] = Node("andexp",p[1:])

def p_relexp(p):
    '''relexp : term
              | term relop relexp
    '''
    p[0] = Node("relexp",p[1:])

def p_term(p):
    '''term : factor
            | factor addop term
    '''
    p[0] = Node("term",p[1:])

def p_addop(p):
    '''addop : '+'
             | '-'
    '''
    p[0] = Node("addop",p[1:])

def p_factor(p):
    '''factor : uniexp
              | uniexp multop factor
    '''
    p[0] = Node("factor",p[1:])

def p_mulop(p):
    '''multop : '*'
              | '/'
              | '%'
    '''
    p[0] = Node("multop",p[1:])


def p_uniexp(p):
    '''uniexp : uniop uniexp
              | postexp
    '''
    p[0] = Node("uniexp",p[1:])

def p_uniop(p):
    '''uniop : '-'
             | '!'
             | incop
             | decop
             | chkop
             | '*'
             | '@'
    '''
    p[0] = Node("uniop",p[1:])


def p_postexp(p):
    '''postexp : entity
               | postexp postfix
    '''
    p[0] = Node("postexp",p[1:])

def p_postfix(p):
    '''postfix : incop
               | decop
    '''
    p[0] = Node("postfix",p[1:])

def p_entity(p):
    '''entity : num
              | id '(' ')'
              | '?'
              | '#'
              | cast
    '''
    p[0] = Node("entity",p[1:])

def p_cast(p):
    "cast : '(' stlist ')'"
    p[0] = Node("cast",p[1:])

def p_error(p):
    print p , "at line " , p.lineno

parser = yacc.yacc()

def parse(data):
    parser.error = 0
    parser.functions = {}
    #p = parser.parse(data)
    p = parser.parse(data,debug=1)
    if parser.error: return None
    p.functions = parser.functions
    return p

if __name__ == '__main__':
    print parse(test).functions