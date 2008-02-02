#coding=gbk
'''
SmallC 语言解释器
工作在抽象语法树上。
SmallC 不允许函数嵌套。
'''
import operator
import copy
import interpretor.smallc.lang as lang

class Namespace:
    def __init__(self,upper = None):
        self.upper = upper
        self.s_const = {}
        self.s_var = {}
        self.s_type = {}
        self.s_function = {}

    def get(self,type,name):
        if hasattr('s_'+self,type) and name in self.__dict__['s_'+self,type]:
            return self.__dict__['s_'+self,type]
        elif self.upper:
            return self.uppper.get(type,name)
        else:
            pass

    def get_const(self,name):
        return self.get("const",name)

    def get_var(self,name):
        return self.get("var",name)

    def get_type(self,name):
        return self.get("type",name)

    def get_function(self,name):
        return self.get("function",name)

    def set(self,type,name,value):
        for s in self.__dict__:
            if s.beginwith("s_") and name in self.__dict__[s]:
                #raise Error
                break
        else:
           self.__dict__["s_" + type][name] = value


class Function(Namespace):
    def __init__(self,ret_type = "",paras = "",upper):
        self.upper = upper
        #self.consts = {}
        self.vars = {}
        #self.types = {}
        #self.functions = {}
        self.params = []

        self.statements = []

    def add_param(self,name,type):
        self.params.append(type)
        self.vars[name] = (type,None)

class Execable:

    def execute(self):
        pass

class LoopStatement(Execable):

    def __init__(self,node,exp,statement = None):
        '''while(exp) st '''
        self.exp = exp
        self.statement = statement

    def execute(self,ns):
        while self.exp.execute(ns):
            if self.statement:
                self.statement.execute(ns)

class CondStatement(Execable):

    def __init__(self,exp,statement,else_statement = None):
        self.exp = exp
        self.statement = statement
        self.else_statement = else_statement

    def execute(self,ns):
        if self.exp.execute():
            self.statement.execute()
        elif self.else_statement:
            self.else_statement.execute()


class Expression(Execable):
    '''表达式计算引擎， 这是解释器很重要的一个部分.
        直接在AST 上执行运算
    '''
    def __init__(self,node):
        pass

    def on_assign(self,node):
        pass

    def on_add(self,node):
        pass

    def execute(self,node):
        pass

def get_built_in_namespace():
    ns = Namespace()
    ns.types = {
        'int':'int',
        'void':'void'
    }
    ns.functions = {
        'print':'print',
        'println':'println'
    }
    return ns


class Parser:
    '''在AST 基础上进一步处理，根据声明语句建立名字空间和函数对象'''
    def __init__(self,ast):
        self.ast = ast
        self.global_ns = get_built_in_namespace()

    def parse(self):
        '''walk the ast , build the golbal namespace'''

        #类定义
        for n in self.ast.get_by_type("classdecls"):
            name = n.get_by_type("id")[0].value
            class_ns = Namespace()
            self.global_ns['name'] = class_ns
            decls = n.get_by_type("decl")
            for x in decls:
                self.on_decl_inside_class(x,class_ns)

        #常量
        for n in self.ast.get_by_type("condecl"):
            for x in n.get_by_type("condef"):
                self.on_condef(x,self.global_ns)

        #变量
        for n in self.ast.get_by_type("vdecl"):
            for x in n.get_by_type("decl"):
                self.on_decl(x,self.global_ns)

        #函数
        for n in self.ast.get_by_type("fdef"):
            self.on_fdef(n,self.global_ns)

    def on_decl(self,node,ns):
        type = self.on_type(node.child(0))
        for n in node.child(1).get_by_type('id'):
            ns.set("var",n.value,(type,None)) #None 不够好。 应该用一个未知的变量来处理。
    def on_decl_inside_class(self,node,cls):

    #函数形参定义
    def on_paradecl(self,node,ns):
        type = self.on_type(node.child(0))
        name = node.child(1).value
        ns.add_param(name,type)

    def on_type(self,node):
        return node

    def on_condef(self,node,ns):
        name = node.child(0)
        value = node.child(-1).value
        if len(node.getChildren()) > 3:
            value = -value
        ns.set("const",name,(None,value)) # type is not need

    def on_fdef(self,node,ns):
        name  = node.child(2).child(0)
        fns = Function()
        fns.ret_type = self.on_type(node.child(1))
        ns.set("function",name,fns)
        for n in node.child(2).get_by_type("paradecl"):
            self.on_paradecl(n,fns)
        for n in node.get_by_type("vdecl"): #vdecl > decllist > decls
            for x in n.get_by_type("decl"):
                self.on_decl(x,fns)
        for n in node.get_by_type("stlist"): # in fact it should be only one
            fns.statements = n.get_by_type("st")

class Interpreter:
    ops = {
        '+' : operator.add,
        '-' : operator.sub,
        '*' : operator.mul,
        '/' : operator.div,
        '%' : operator.mod,
        '<' : operator.lt,
        '>' : operator.gt,
        '<=': operator.le,
        '>=': operator.ge
    }
    uniops = {
        '-' : operator.neg,
        '!' : operator.not_,
        'chk' : lambda x : x
    }
    def __init__(self,ast,global_ns):
        self.ast = ast
        self.global_ns = global_ns
        self.current_ns = None

    def run(self):
        pass

    def on_statement(self,node):
        if node.type == "cond":
            self.on_cond(node)
        elif node.type == "loop":
            self.on_loop(node)
        elif node.type == "exp":
            self.on_exp(node)

    def on_cond(self,node):
        exp = node.child(2)
        st = node.child(4)
        else_st = node.child_or_none(6)
        if self.on_exp(exp):
            self.on_statement(st)
        elif else_st:
            self.on_statement(else_st)

    def on_loop(self,node):
        exp = node.child(2)
        st = node.child_or_none(4)

        while self.on_exp(exp):
            if st:
                self.on_statement(exp)

    def on_exp(self,node):
        if node.child_or_none(1):
            lhs = self.on_orexp(node.child(0))
            rhs = self.on_orexp(node.child(2))
            lhs.assign(rhs)
            return lhs
        else:
            return self.on_orexp(node.child(0))

    def on_orexp(self,node):
        if node.child_or_none(1):
            lhs = self.on_orexp(node.child(0))
            rhs = self.on_andexp(node.child(2))
            r = Variable(self.current_ns)
            if lhs.value != 0 or rhs.value != 0:
                r.value = 1
            else:
                r.value = 0
            return r
        else:
            return self.on_andexp(node.child(0))

    def on_andexp(self,node):
        if node.child_or_none(1):
            lhs = self.on_andexp(node.child(0))
            rhs = self.on_relexp(node.child(2))
            r = Variable(self.current_ns)
            if lhs.value != 0 and rhs.value != 0:
                r.value = 1
            else:
                r.value = 0
            return r
        else:
            return self.on_relexp(node.child(0))

    def on_relexp(self,node):
        if node.child_or_none(1):
            lhs = self.on_relexp(node.child(0))
            rhs = self.on_term(node.child(2))
            relop = node.child(1).child(0).value
            r = Variable(self.current_ns)
            r.value = self.ops[relop](lhs.value,rhs.value)
            return r
        else:
            return self.on_term(node.child(0))

    def on_term(self,node):
        if node.child_or_none(1):
            lhs = self.on_term(node.child(0))
            rhs = self.on_factor(node.child(2))
            addop = node.child(1).child(0).value
            r = Variable(self.current_ns)
            r.value = self.ops[addop](lhs.value,rhs.value)
            return r
        else:
            return self.on_factor(node.child(0))

    def on_factor(self,node):
        if node.child_or_none(1):
            lhs = self.on_factor(node.child(0))
            rhs = self.on_uniexp(node.child(2))
            multop = node.child(1).child(0).value
            r = Variable(self.current_ns)
            r.value = self.ops[multop](lhs.value,rhs.value)
            return r
        else:
            return self.on_uniexp(node.child(0))

    def on_uniexp(self,node):
        if node.child_or_none(1):
            uniop = node.child(0).child(0).value
            uniexp = self.on_uniexp(node.child(1))
            if uniop == '++':
                uniexp.value += 1
                return uniexp
            elif uniop == '--':
                uniexp.value -= 1
                return uniexp
            else:
                r = Variable(self.current_ns)
                r.value = self.uniops[uniop](uniexp.value)
                return r
        else:
            return self.on_postexp(node.child(0))

    #TODO error
    def on_postexp(self,node):
        if node.child_or_none(1):
            postexp = self.on_postexp(node.child(0))
            postfix = node.child(1)
            if isinstance(node,Node):
                pass
            else:
                if postfix == '++':
                    ret = postexp.copy()
                    postexp.value += 1
                    return uniexp
                elif uniop == '--':
                    uniexp.value -= 1
                    return uniexp
        else:
            return self.on_entity(node.child(0))