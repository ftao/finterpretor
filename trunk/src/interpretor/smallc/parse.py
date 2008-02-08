#coding=gbk
from ply import yacc

from interpretor.smallc.lex import *
from interpretor.smallc.ast import Node

start = 'prog'
def p_empty(p):
    "empty : "
    pass

#程序
def p_prog(p):
    '''prog : class_decls const_decls var_decls fdefs
    '''
    p[0] = Node("prog", filter(lambda x : isinstance(x, Node) , p[1:]))

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
    p[0] = Node("classdecl",p[1:])

def p_decllist(p):
    '''decllist : decl ';' decllist
                | decl
    '''
    if len(p) > 2:
        p[0] = Node("declist",[p[1]] + p[3].getChildren())
    else:
        p[0] = Node("declist",p[1:])

def p_decl(p):
    "decl : type idlist"
    p[0] = Node("decl",p[1:])

#类型
def p_type(p):
    '''type : type '[' ']'
            | id
    '''
    if len(p) > 2:
        p[0] = Node("type",p[1].getChildren() + p[2:])
    else:
        p[0] = Node("type",p[1:])


def p_idlist(p):
    '''idlist : id ',' idlist
              | id
    '''
    if len(p) > 2:
        p[0] = Node("idlist",[p[1]] + p[3].getChildren())
    else:
        p[0] = Node("idlist",p[1:])


#可能的常量声明
def p_const_decls(p):
    '''const_decls : condecl ';'
                   | empty
    '''
    p[0] = p[1]


def p_condecl(p):
    '''condecl : condecl ',' condef
               | kw_const condef
    '''
    if len(p) > 3:
        p[0] = Node("condecl",p[1].getChildren() + p[3:])
    else:
        p[0] = Node("condecl",p[1:])

#常量定义
def p_condef(p):
    '''condef : id '=' num
              | id '=' '-' num
    '''
    p[0] = Node("condef",p[1:])


#变量声明
def p_var_decls(p):
    '''var_decls : vdecl
                 | empty
    '''
    p[0] = p[1]

def p_vdecl(p):
    "vdecl : kw_var decllist kw_end"
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
    p[0] = Node("fdef", p[1:])
    #p.parser.functions[p[2]] = p[4] #函数名对应的函数体

def p_head(p):
    '''head : id '(' ')'
            | id '(' paralist ')'
    '''
    p[0] = Node("head", p[1:])

def p_paralist(p):
    '''paralist : paradecl
                | paradecl ',' paralist
    '''
    if len(p) > 2:
        p[0] = Node("paralist",[p[1]] + p[3].getChildren())
    else:
        p[0] = Node("paralist",p[1:])

def p_paradecl(p):
    "paradecl : type id "
    p[0] = Node("paradecl", p[1:])

def p_funbody(p):
    '''funbody : vdecl stlist
                | stlist
    '''
    p[0] = Node("funcbody", p[1:])



def p_stlist(p):
    '''stlist : st ';' stlist
              | st
    '''
    p[0] = Node("stlist", p[1:])

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
             | orexp  orop andexp
    '''
    p[0] = Node("orexp",p[1:])

def p_andexp(p):
    '''andexp : relexp
              | andexp andop relexp
    '''
    p[0] = Node("andexp",p[1:])

def p_relexp(p):
    '''relexp : term
              | relexp relop term
    '''
    p[0] = Node("relexp",p[1:])

def p_relop(p):
    '''relop : eqop
             | neop
             | ltop
             | gtop
             | leop
             | geop
    '''
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
    p[0] = Node("postfix",p[1:])

def p_apara(p):
    '''apara : '(' explist ')'
             | '(' ')'
    '''
    p[0] = Node("apara",p[1:])


def p_explist(p):
    '''explist : exp
               | exp ',' explist
    '''
    if len(p) > 2:
        p[0] = Node("explist",[p[1]] + p[3].getChildren())
    else:
        p[0] = Node("explist",p[1:])

def p_sub(p):
    "sub : '[' exp ']'"
    p[0] = Node("sub",p[1:])

def p_aselect(p):
    "aselect : '.' id"
    p[0] = Node("aselect",p[1:])

def p_tcast(p):
    "tcast : ':' type"
    p[0] = Node("tcast",p[1:])

def p_entity(p):
    '''entity : id
              | num
              | cast
              | alloc
              | '?'
    '''
    p[0] = Node("entity",p[1:])

def p_cast(p):
    "cast : '(' stlist ')'"
    p[0] = Node("cast",p[1:])

def p_alloc(p):
    '''alloc : kw_new type
             | kw_new type '[' exp ']'
    '''
    p[0] = Node("alloc",p[1:])

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
    n =  parse(test)
    print n.get_by_type("decl")