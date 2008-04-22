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

class BaseSementicAction:

    def on_node(self, node):
        pass

    def on_decl(self,node,ns):
        pass

    def on_decl_inside_class(self,node,struct):
        pass

    def on_paradecl(self,node,ns):
        pass

    def on_type(self,node):
        pass

    def on_condef(self,node,ns):
        pass

    def on_fdef(self,node,ns):
        pass

    def on_statement(self, *node):
        return node

    def on_cond(self, *node):
        pass

    def on_loop(self,node):
        pass

    def on_exp(self,node):
        pass

    def on_orexp(self,node):
        pass

    def on_andexp(self,node):
        pass

    def on_relexp(self,node):
        pass

    def on_term(self,node):
        pass

    def on_factor(self,node):
        pass

    def on_uniexp(self,node):
        pass

    def on_postexp(self,node):
        pass

    def on_type(self,node):
        pass

    def on_entity(self,node):
        pass

    def on_cast(self,node):
        pass

    def on_alloc(self,node):
        pass

    def on_apara(self,node):
        pass

    def on_token(self,node):
        pass



