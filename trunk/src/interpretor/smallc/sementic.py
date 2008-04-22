#coding=utf8
#$Id$
#DONT'T READ OR USE THIS FILE
'''定义SmallC 的语义
1. 静态语义
首先是最简单的操作的类型匹配
'''

import interpretor.smallc.lang

#类型约束
#这个应该作为语言定义的一部分
#一条约束规则应该包含如下的内容
# * 操作符
# * 约束规则列表
#用一个简单的列表就可以

type_requirements = {}

#这里在全局字典 type_requirements 加入对应的条目，
#在静态类型检查时将要用到这个
def add_type_requirement(op_name, requirement):
    if not type_requirements.has_key(op_name):
        type_requirements[op_name] = set()
    type_requirements[op_name].add(requirement)

def check_type_requirement(op_name, *operands):
    ret = True
    for func in type_requirements['op_name']:
        if not func(*operands):
            ret = False
            break
    return ret


#这个文件定义了语义动作

class BaseASTWalker:

    def on_prog(self, node):
        return node.child(0)

    def on_class_decls(self, node):
        return node.child(0)

    def on_classdecl(self, node):
        return node.child(0)

    def on_decllist(self, node):
        return node.child(0)

    def on_decl(self, node):
        return node.child(0)

    def on_type(self, node):
        return node.child(0)

    def on_idlist(self, node):
        return node.child(0)

    def on_condecl(self, node):
        return node.child(0)

    def on_condef(self, node):
        return node.child(0)

    def on_vdecl(self, node):
        return node.child(0)

    def on_fdefs(self, node):
        return node.child(0)

    def on_fdef(self, node):
        return node.child(0)

    def on_head(self, node):
        return node.child(0)

    def on_paralist(self, node):
        return node.child(0)

    def on_paradecl(self, node):
        return node.child(0)

    def on_funbody(self, node):
        return node.child(0)

    def on_stlist(self, node):
        return node.child(0)

    def on_st(self, node):
        return node.child(0)

    def on_cond(self, node):
        return node.child(0)

    def on_loop(self, node):
        return node.child(0)

    def on_exp(self, node):
        return node.child(0)

    def on_orexp(self, node):
        return node.child(0)

    def on_andexp(self, node):
        return node.child(0)

    def on_relexp(self, node):
        return node.child(0)

    def on_relop(self, node):
        return node.child(0)

    def on_term(self, node):
        return node.child(0)

    def on_addop(self, node):
        return node.child(0)

    def on_factor(self, node):
        return node.child(0)

    def on_mulop(self, node):
        return node.child(0)

    def on_uniexp(self, node):
        return node.child(0)

    def on_uniop(self, node):
        return node.child(0)

    def on_postexp(self, node):
        return node.child(0)

    def on_postfix(self, node):
        return node.child(0)

    def on_apara(self, node):
        return node.child(0)

    def on_explist(self, node):
        return node.child(0)

    def on_sub(self, node):
        return node.child(0)

    def on_aselect(self, node):
        return node.child(0)

    def on_tcast(self, node):
        return node.child(0)

    def on_entity(self, node):
        return node.child(0)

    def on_cast(self, node):
        return node.child(0)

    def on_alloc(self, node):
        return node.child(0)




