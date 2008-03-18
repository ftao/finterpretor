#coding=utf8
from ply import yacc

from interpretor.kernelc.lex import *
from interpretor.ast import Node,all_to_node

start = 'prog'

def p_prog(p):
    '''prog : prog fdef
            | fdef
    '''
    if len(p) > 2 :
        p[0] = Node("prog", p[1].getChildren() + [p[2]])
    else:
        p[0] = Node("prog", [p[2]])

def p_fdef(p):
    "fdef : kw_func id '{' stlist '}'"
    all_to_node(p)
    p[0] = Node("fdef", p[1:])


def p_stlist(p):
    '''stlist : stlist ';' st
              | st
    '''
    all_to_node(p)
    if len(p) > 3 :
        p[0] = Node("stlist", p[1].getChildren() + [p[3]])
    else:
        p[0] = Node("stlist", p[1:])

def p_st(p):
    '''st : exp
          | cond
          | loop
    '''
    p[0] = Node("st",p[1:])

#def p_print_st(p):
#    ''' print_st : io_print '(' exp ')'
#                 | io_print '(' ')'
#    '''
#    all_to_node(p)
#    p[0] = Node("print_st",p[1:])
#
#def p_println_st(p):
#    ''' println_st : io_println '(' exp ')'
#                   | io_println '(' ')'
#    '''
#    all_to_node(p)
#    p[0] = Node("println_st",p[1:])


def p_cond(p):
    '''cond : kw_if '(' exp ')' st
            | kw_if '(' exp ')' st  kw_else st
    '''
    all_to_node(p)
    p[0] = Node("cond",p[1:])

def p_loop(p):
    '''loop : kw_while '(' exp ')'
            | kw_while '(' exp ')' st
    '''
    all_to_node(p)
    p[0] = Node("loop",p[1:])

def p_exp(p):
    '''exp : orexp
           | orexp '=' orexp
    '''
    all_to_node(p)
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
    all_to_node(p)
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
    all_to_node(p)
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
             | '#'
             | io_print
             | io_println
    '''
    all_to_node(p)
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
    all_to_node(p)
    p[0] = Node("postfix",p[1:])

def p_entity(p):
    '''entity : num
              | id '(' ')'
              | '?'
              | '#'
              | cast
    '''
    all_to_node(p)
    p[0] = Node("entity",p[1:])

def p_cast(p):
    "cast : '(' stlist ')'"
    all_to_node(p)
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
