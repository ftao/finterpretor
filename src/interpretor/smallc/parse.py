#coding=gbk
import sys

from ply import yacc
from interpretor.smallc.lex import *
from interpretor.smallc.ast import Node,Leaf
import interpretor.smallc.error as error

#def sall_to_nodee(func):
#    def wrapped(p):
#        for i in range(len(p)):
#            if p[i] and not isinstance(p[i], Node):
#                p[i] = Leaf(child, p.lineno(i), p.lexpos(i))
#        return func(p)
#    wrapped.__doc__ = func.__doc__
#
#    return wrapped

def all_to_node(p):
    for i in range(len(p)):
        if p[i] is not None and not isinstance(p[i], Node):
            p[i] = Leaf(p[i], p.lineno(i), p.lexpos(i))

start = 'prog'
def p_empty(p):
    "empty : "
    pass

#程序
def p_prog(p):
    '''prog : class_decls const_decls var_decls fdefs
    '''
    p[0] = Node("prog",p[1:])

#类声明s
def p_class_decls(p):
    '''class_decls : class_decls classdecl
                   | classdecl
                   | empty
    '''
    if len(p) > 2 :
        if p[1]:
            p[0] = Node("class_decls", p[1].getChildren() + [p[2]])
        else:
            p[0] = Node("class_decls", [p[2]])
    elif p[1]:
        p[0] = Node("class_decls",[p[1]])




def p_classdecl(p):
    "classdecl : kw_class id '{' decllist '}'"
    all_to_node(p)
    p[0] = Node("classdecl",p[1:])


def p_decllist(p):
    '''decllist : decl ';' decllist
                | decl
    '''
    all_to_node(p)
    if len(p) > 2:
        p[0] = Node("decllist",[p[1]] + p[3].getChildren())
    else:
        p[0] = Node("decllist",p[1:])

def p_decl(p):
    "decl : type idlist"
    p[0] = Node("decl",p[1:])

#类型

def p_type(p):
    '''type : type '[' ']'
            | id
    '''
    all_to_node(p)
    #the final ast should like  id {'[' ']'}
    if len(p) > 2:
        p[0] = Node("type",p[1].getChildren() + p[2:])
    else:
        p[0] = Node("type",p[1:])


def p_idlist(p):
    '''idlist : id ',' idlist
              | id
    '''
    all_to_node(p)
    if len(p) > 2:
        p[0] = Node("idlist",[p[1]] + p[3].getChildren())
    else:
        p[0] = Node("idlist",p[1:])


#可能的常量声明

def p_const_decls(p):
    '''const_decls : condecl ';'
                   | empty
    '''
    all_to_node(p)
    p[0] = p[1]


def p_condecl(p):
    '''condecl : condecl ',' condef
               | kw_const condef
    '''
    all_to_node(p)
    if len(p) > 3:
        p[0] = Node("condecl",p[1].getChildren() + p[3:])
    else:
        p[0] = Node("condecl",p[1:])

#常量定义

def p_condef(p):
    '''condef : id '=' num
              | id '=' '-' num
    '''
    all_to_node(p)
    p[0] = Node("condef",p[1:])


#变量声明
def p_var_decls(p):
    '''var_decls : vdecl
                 | empty
    '''
    p[0] = p[1]


def p_vdecl(p):
    "vdecl : kw_var decllist kw_end"
    all_to_node(p)
    p[0] = Node("vdecl",p[1:])


#函数定义s
def p_fdefs(p):
    ''' fdefs : fdef fdefs
              | fdef
    '''
    if len(p) > 2:
        p[0] = Node("fdefs",[p[1]] + p[2].getChildren())
    else:
        p[0] = Node("fdefs",p[1:])


def p_fdef(p):
    "fdef : kw_func type head '{' funbody '}'"
    all_to_node(p)
    p[0] = Node("fdef", p[1:])



def p_head(p):
    '''head : id '(' ')'
            | id '(' paralist ')'
    '''
    all_to_node(p)
    p[0] = Node("head", p[1:])


def p_paralist(p):
    '''paralist : paradecl
                | paradecl ',' paralist
    '''
    all_to_node(p)
    if len(p) > 2:
        p[0] = Node("paralist",[p[1]] + p[3].getChildren())
    else:
        p[0] = Node("paralist",p[1:])


def p_paradecl(p):
    "paradecl : type id "
    all_to_node(p)
    p[0] = Node("paradecl", p[1:])


def p_funbody(p):
    '''funbody : vdecl stlist
                | stlist
    '''
    p[0] = Node("funbody", p[1:])



def p_stlist(p):
    '''stlist : st ';' stlist
              | st
    '''
    all_to_node(p)
    if len(p) > 2:
        p[0] = Node("stlist",[p[1]] + p[3].getChildren())
    else:
        p[0] = Node("stlist",p[1:])

def p_st(p):
    '''st : exp
          | cond
          | loop
    '''
    p[0] = Node("st",p[1:])



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
             | orexp  orop andexp
    '''
    all_to_node(p)
    p[0] = Node("orexp",p[1:])


def p_andexp(p):
    '''andexp : relexp
              | andexp andop relexp
    '''
    all_to_node(p)
    p[0] = Node("andexp",p[1:])


def p_relexp(p):
    '''relexp : term
              | relexp relop term
    '''
    all_to_node(p)
    p[0] = Node("relexp",p[1:])


def p_relop(p):
    '''relop : eqop
             | neop
             | ltop
             | gtop
             | leop
             | geop
    '''
    all_to_node(p)
    p[0] = p[1]


def p_term(p):
    '''term : factor
            | term addop factor
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
              | factor multop uniexp
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
               | apara
               | sub
               | aselect
               | tcast
    '''
    all_to_node(p)
    p[0] = Node("postfix",p[1:])


def p_apara(p):
    '''apara : '(' explist ')'
             | '(' ')'
    '''
    all_to_node(p)
    p[0] = Node("apara",p[1:])


def p_explist(p):
    '''explist : exp
               | exp ',' explist
    '''
    all_to_node(p)
    if len(p) > 2:
        p[0] = Node("explist",[p[1]] + p[3].getChildren())
    else:
        p[0] = Node("explist",p[1:])


def p_sub(p):
    "sub : '[' exp ']'"
    all_to_node(p)
    p[0] = Node("sub",p[1:])


def p_aselect(p):
    "aselect : '.' id"
    all_to_node(p)
    p[0] = Node("aselect",p[1:])


def p_tcast(p):
    "tcast : ':' type"
    all_to_node(p)
    p[0] = Node("tcast",p[1:])


def p_entity(p):
    '''entity : id
              | num
              | cast
              | alloc
              | '?'
    '''
    all_to_node(p)
    p[0] = Node("entity",p[1:])


def p_cast(p):
    "cast : '(' stlist ')'"
    all_to_node(p)
    p[0] = Node("cast",p[1:])


def p_alloc(p):
    '''alloc : kw_new type
             | kw_new type '[' exp ']'
    '''
    all_to_node(p)
    p[0] = Node("alloc",p[1:])


def p_error(p):
    #print >>sys.stderr,"parser error at line %d token '%s'" %(p.lineno, p.value)
    raise error.ParseError(p)

parser = yacc.yacc()

def parse(data):
    p = parser.parse(data)
    return p

if __name__ == '__main__':
    n =  parse(test)
    print len(n.query("vdecl>decllist>decl"))
    print len(n.query("class_decls>classdecl"))
