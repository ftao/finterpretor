#coding=gbk
import sys

from ply import yacc
from interpretor.ooc.lex import *
from interpretor.ooc.ast import Node,Leaf


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
    '''prog : prog classdecl
            | classdecl
    '''
    if len(p) > 2:
        p[0] = Node("prog",p[1].getChildren() + [p[2]])
    else:
        p[0] = Node("prog",[p[1]])



def p_classdecl(p):
    "classdecl : kw_class pos_abstract id pos_superclass '{' pos_condecl pos_static pos_private pos_public pos_redef '}'"
    all_to_node(p)
    p[0] = Node("classdecl",p[1:])


def p_pos_abstract(p):
    '''pos_abstract : kw_abstract
                    | empty
    '''
    all_to_node(p)
    if p[1] != None:
        p[0] = Node("pos_abstract",p[1:])
    else:
        p[0] = p[1]

def p_pos_superclass(p):
    '''pos_superclass : ':' id
                      | empty
    '''
    all_to_node(p)
    if len(p) > 2:
        p[0] = Node("pos_superclass",p[1:])
    else:
        p[0] = p[1]

#可能的常量声明
def p_pos_condecl(p):
    '''pos_condecl : condecl ';'
                   | empty
    '''
    all_to_node(p)
    if p[1] != None:
        p[0] = Node("pos_condecl",p[1:])
    else:
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


def p_pos_static(p):
    '''pos_static : kw_static member
                  | empty
    '''
    all_to_node(p)
    if p[1] != None:
        p[0] = Node("pos_static",p[1:])
    else:
        p[0] = p[1]

def p_pos_private(p):
    '''pos_private : kw_private member
                  | empty
    '''
    all_to_node(p)
    if p[1] != None:
        p[0] = Node("pos_private",p[1:])
    else:
        p[0] = p[1]

def p_pos_public(p):
    '''pos_public : kw_public member
                  | empty
    '''
    all_to_node(p)
    if p[1] != None:
        p[0] = Node("pos_public",p[1:])
    else:
        p[0] = p[1]

def p_pos_redef(p):
    '''pos_redef : kw_redef cfdef_list
                 | kw_redef
                 | empty
    '''
    all_to_node(p)
    if p[1] != None:
        p[0] = Node("pos_redef",p[1:])
    else:
        p[0] = p[1]

def p_cfdefs(p):
    '''cfdef_list : cfdef_list cfdef
                  | cfdef
    '''
    if len(p) > 2:
        p[0] = Node("cfdef_list",p[1].getChildren() + [p[2]])
    else:
        p[0] = Node("cfdef_list",p[1:])


def p_member(p):
    '''member : vdecl fdefs
              | vdecl
              | fdefs
              | empty
    '''
    p[0] = Node("member",p[1:])

def p_vdecl(p):
    "vdecl : kw_var decllist kw_end"
    all_to_node(p)
    p[0] = Node("vdecl",p[1:])


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
    '''fdef : afdef
            | cfdef
    '''
    p[0] = Node("fdef",p[1:])


def p_afdef(p):
    '''afdef : kw_func kw_abstract type id '(' type_list ')'
             | kw_func kw_abstract type id '('  ')'
    '''
    all_to_node(p)
    p[0] = Node("afdef", p[1:])

def p_typelist(p):
    '''type_list : type_list ',' type
                 | type
    '''
    if len(p) > 2:
        p[0] = Node("type_list",p[1].getChildren() + [p[3]])
    else:
        p[0] = Node("type_list",p[1:])


def p_cfdef(p):
    "cfdef : kw_func type head '{' funbody '}'"
    all_to_node(p)
    p[0] = Node("cfdef", p[1:])



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
               | index
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


def p_index(p):
    "index : '[' exp ']'"
    all_to_node(p)
    p[0] = Node("index",p[1:])


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
    print >>sys.stderr,"parser error at line %d token '%s'" %(p.lineno, p.value)
    sys.exit()

parser = yacc.yacc()

def parse(data):
    p = parser.parse(data,debug=1)
    return p

if __name__ == '__main__':
    n =  parse(test)
    print len(n.query("classdecl>pos_static"))
