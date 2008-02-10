#coding=gbk
'''
SmallC 语言解释器
工作在抽象语法树上。
SmallC 不允许函数嵌套。
'''
import operator
import copy
import sys
import interpretor.smallc.lang as lang
from interpretor.smallc.parse import parse
from interpretor.smallc.lex import test
from interpretor.smallc.ast import Node,Leaf
import interpretor.smallc.error

def copy_ns(ns_dict):
    ret = copy.copy(ns_dict)
    for x in ret:
        ret[x] = copy.copy(ns_dict[x])
    return ret


class Namespace:
    def __init__(self,upper = None):
        self.upper = upper
        self.ns = {}
        self.name = "global"

    def get(self, name):
        if name in self.ns:
            return self.ns[name]
        elif self.upper:
            return self.upper.get(name)
        else:
            #print self.ns
            raise error.NameError(name)

    def __getitem__(self, key):
        return self.get(key)

    def set(self, name, value):
        #print self.name,id(self.ns)
        if name in self.ns:
            raise error.MultipleError(name)
        else:
            self.ns[name] = value

    def __setitem__(self, key, value):
        self.set(key, value)

    def __repr__(self):
        return "Namespace %s" %(self.name)

class Function(Namespace):
    def __init__(self,name,upper,ret_type = lang.void):
        self.name = name
        self.upper = upper
        self.ns = {}
        self.ret_type = ret_type
        self.params = []
        self.statements = []

    def add_param(self,name,type):
        self.params.append(name)
        self.set(name,lang.Object(type))

    def freeze(self):
        self.ns_org = copy_ns(self.ns)
        #print "freeze" ,self.ns_org

    def set_param(self, name, value):
        if name not in self.ns:
            raise NameError(name)
        else:
            self.ns[name].op("assign",value)

    def set(self, name, value):
        #print self.name,id(self.ns)
        if name in self.ns:
            raise MultipleError(name)
        else:
            self.ns[name] = value

    def call(self,args,inter):
        #print "in function " , self.name
        #print "ret type " , self.ret_type
        #print "BEFOR CALL current ns for function %s : %s" %(self.name,self.ns)
        ns_now = self.ns
        self.ns = copy_ns(self.ns_org)
        #print "call self.ns" , self.ns
        #print "call self.ns_org", self.ns_org
        old_current = inter.current_ns
        inter.current_ns = self
        #print id(old_current),id(self)
        #print id(old_current.ns),id(self.ns)
        #ret = lang.Object(lang.void)
        #print args
        for i in range(len(self.params)):
            self.set_param(self.params[i], args[i])
        for st in self.statements:
            #print st
            ret = inter.on_statement(st)
        self.ns = ns_now
        inter.current_ns = old_current
        #print "ret value %s -> %s" %(ret, ret.op("tcast", self.ret_type))
        #print "return from function " , self.name
        #print "current ns for function %s : %s" %(self.name,self.ns)
        return ret.op("tcast", self.ret_type)

    def __repr__(self):
        #return "Namespace in function %s : %s" %(self.name, repr(self.ns))
        return "Function %s " %self.name

class PrintFunc(Function):
    def __init__(self):
        self.name = "print"

    def call(self,args,inter):
        #print "in function print"
        for x in args:
            x.op("print")
        return lang.Object(lang.void)

    def __repr__(self):
        return "function %s" %(self.name)

class PrintlnFunc(Function):
    def __init__(self):
        self.name = "println"

    def call(self,args,inter):
        #print "in function println"
        for x in args:
            x.op("print")
        print
        return lang.Object(lang.void)
    def __repr__(self):
        return "function %s" %(self.name)


inputFlags = {
    "InputBuff" : "",
    "isEOF" : 0
}
class ReadFunc(Function):
    def __init__(self,input):
        self.name = "read"
        self.input = input
    def call(self,args,inter):
        if self.input["InputBuff"]:
            inp = self.input["InputBuff"]
            try:
                self.input["InputBuff"] = ""
                self.input["InputBuff"] = raw_input()
            except EOFError,e:
                self.input["isEOF"] = 1
        else:
            inp = raw_input()
        return lang.Object(lang.intType, int(inp))
    def __repr__(self):
        return "function %s" %(self.name)

class EofFunc(Function):
    def __init__(self,input):
        self.name = "eof"
        self.input = input
    def call(self,args,inter):
        if not self.input["InputBuff"] and not self.input["isEOF"]:
            try:
                self.input["InputBuff"] = raw_input()
            except EOFError,e:
                self.input["isEOF"] = 1
        return lang.Object(lang.intType, self.input["isEOF"])
    def __repr__(self):
        return "function %s" %(self.name)

def get_built_in_namespace():
    ns = Namespace()
    ns.ns = {
        'int':lang.intType,
        'void':lang.void,
        'null':lang.null,
        'print':PrintFunc(),
        'println':PrintlnFunc(),
        'read':ReadFunc(inputFlags),
        'eof':EofFunc(inputFlags)
    }
    return ns


class MoreParser:
    '''在AST 基础上进一步处理，根据声明语句建立名字空间和函数对象'''
    def __init__(self,ast):
        self.ast = ast
        self.global_ns = get_built_in_namespace()
        self.current_ns = self.global_ns

    def parse(self):
        '''walk the ast , build the golbal namespace'''

        #for x in self.ast.getChildren():
        #    print x.type

        #类定义
        for n in self.ast.query("class_decls>classdecl"):
            name = n.child(1).value
            struct = lang.Struct(name)
            self.global_ns.set(name, struct)


        for n in self.ast.query("class_decls>classdecl"):
            name = n.child(1).value
            struct = self.global_ns.get(name)
            for x in n.child(3):
                self.on_decl_inside_class(x,struct)

        #常量
        for n in self.ast.query("condecl>condef"):
            self.on_condef(n,self.global_ns)

        #变量
        for decl in self.ast.query("vdecl>decllist>decl"):
            self.on_decl(decl,self.global_ns)

        #函数
        for n in self.ast.query("fdefs>fdef"):
            self.on_fdef(n,self.global_ns)

    def on_decl(self,node,ns):
        type = self.on_type(node.child(0))
        for id in node.child(1):
            ns.set(id.value,lang.Object(type))

    def on_decl_inside_class(self,node,struct):
        type = self.on_type(node.child(0))
        #print struct
        for id in node.child(1):
            #print "on decl inside class" ,id.value
            struct.add_member(type,id.value)

    #函数形参定义
    def on_paradecl(self,node,ns):
        type = self.on_type(node.child(0))
        name = node.child(1).value
        ns.add_param(name,type)

    def on_type(self,node):
        base = node.child(0).value
        base_type = self.current_ns.get(base)
        if not base_type:
            pass # raise Error
        else:
            if len(node) > 1:
                dim = (len(node) - 1)/2
                return lang.Array(base_type, dim)
            else:
                return base_type

    def on_condef(self,node,ns):
        #print node
        name = node.child(0).value
        value = node.child(-1).value
        if len(node) > 3:
            value = -value
        ns.set(name,lang.ConstObject(lang.intType,value)) # type use lang.intType

    def on_fdef(self,node,ns):
        name  = node.child(2).child(0).value
        fns = Function(name,self.current_ns)
        fns.ret_type = self.on_type(node.child(1))
        ns.set(name,fns)

        for para in node.query("head>paralist>paradecl"):
            self.on_paradecl(para,fns)
        for decl in node.query("funbody>vdecl>decllist>decl"):#vdecl > decllist > decls
            self.on_decl(decl,fns)
        fns.statements = node.query("funbody>stlist>st")
        fns.freeze()

class Interpreter:

    def __init__(self,ast,global_ns):
        self.ast = ast
        self.global_ns = global_ns
        self.current_ns = None

    def run(self):
        self.current_ns = self.global_ns
        self.current_ns.get("main").call([],self)

    def on_statement(self,node):
        node = node.child(0)
        if node.type == "cond":
            return self.on_cond(node)
        elif node.type == "loop":
            return self.on_loop(node)
        elif node.type == "exp":
            return self.on_exp(node)

    def on_cond(self,node):
        print node
        exp = node.child(2)
        st = node.child(4)
        if self.on_exp(exp):
            return self.on_statement(st)
        elif len(node) > 6:
            return self.on_statement(node.child(6))
        return lang.Object(lang.void)

    def on_loop(self,node):
        print node
        exp = node.child(2)
        ret = lang.Object(lang.void)
        while self.on_exp(exp):
            if len(node) > 4:
                ret = self.on_statement(node.child(4))
        return ret

    def on_exp(self,node):
        print node
        if len(node) > 1:
            lhs = self.on_orexp(node.child(0))
            rhs = self.on_orexp(node.child(2))
            return lhs.op("assign",rhs)
        else:
            return self.on_orexp(node.child(0))

    def on_orexp(self,node):
        if len(node) > 1:
            lhs = self.on_orexp(node.child(0))
            rhs = self.on_andexp(node.child(2))
            return lhs.op("or",rhs)
        else:
            return self.on_andexp(node.child(0))

    def on_andexp(self,node):
        if len(node) > 1:
            lhs = self.on_andexp(node.child(0))
            rhs = self.on_relexp(node.child(2))
            return lhs.op("and",rhs)
        else:
            return self.on_relexp(node.child(0))

    def on_relexp(self,node):
        if len(node) > 1:
            lhs = self.on_relexp(node.child(0))
            rhs = self.on_term(node.child(2))
            m = {
             '==':'eq',
             '!=':'ne',
             '<':'lt',
             '>':'gt',
             '<=':'le',
             '>=':'ge'
            }
            #print "relop : " ,node.child(1)
            relop = m[node.child(1).value]
            return lhs.op(relop,rhs)
        else:
            return self.on_term(node.child(0))

    def on_term(self,node):
        if len(node) > 1:
            lhs = self.on_term(node.child(0))
            rhs = self.on_factor(node.child(2))
            op = {'+':'add','-':'minus'}[node.child(1).child(0).value]
            return lhs.op(op,rhs)
        else:
            return self.on_factor(node.child(0))

    def on_factor(self,node):
        if len(node) > 1:
            lhs = self.on_factor(node.child(0))
            rhs = self.on_uniexp(node.child(2))
            op =  {'*':'mul','/':'div','%':'mod'}[node.child(1).child(0).value]
            return lhs.op(op,rhs)
        else:
            return self.on_uniexp(node.child(0))

    def on_uniexp(self,node):
        if len(node) > 1:
            uniop = {'++':'inc','--':'dec',
                    '-':'minus_','!':'not','chk':'chk'}[node.child(0).child(0).value]
            uniexp = self.on_uniexp(node.child(1))
            return uniexp.op(uniop)
        else:
            return self.on_postexp(node.child(0))

    #TODO error
    def on_postexp(self,node):
        #print "on postexp" ,node
        if len(node) > 1:
            postexp = self.on_postexp(node.child(0))
            postfix = node.child(1).child(0)
            if postfix.type == 'apara':
                if len(postfix) == 2:
                    return postexp.call([],self)
                else:
                    return postexp.call(self.on_apara(postfix),self)
            elif postfix.type =='sub':
                return postexp.op("index",self.on_exp(postfix.child(1)))
            elif postfix.type == 'aselect':
                return postexp.op("member",postfix.child(1).value)
            elif postfix.type == 'tcast':
                return postexp.op("tcast",self.on_type(postfix.child(1)))
            if isinstance(postfix,Leaf):
                if postfix.value == '++':
                    return postexp.op("inc_")
                elif postfix.value == '--':
                    return postexp.op("dec_")

        else:
            return self.on_entity(node.child(0))



    def on_type(self,node):
        base = node.child(0).value
        base_type = self.current_ns.get(base)
        if len(node) > 1:
            dim = len(node) - 1
            return lang.Array(base_type, dim)
        else:
            return base_type

    def on_entity(self,node):
        entity = node.child(0)
        #print entity
        if entity.type == "cast":
            return self.on_cast(entity)
        elif entity.type == "alloc":
            return self.on_alloc(entity)
        elif entity.value == "?": # input
            return self.current_ns.get("read").call([],self)
        elif isinstance(entity,Leaf):
            entity = entity.value
            if isinstance(entity,str):
                return self.current_ns.get(entity)
            elif isinstance(entity,int):
                return lang.Object(lang.intType, entity)
    def on_cast(self,node):
        '''cast 的语义？ 最后一个statement 的值'''
        for x in node.query("stlist>st"):
            ret = self.on_statement(x)
        return ret

    def on_alloc(self,node):
        if len(node) == 2:
            ret =  self.on_type(node.child(1)).alloc()
        else:
            ret = self.on_type(node.child(1)).alloc(self.on_exp(node.child(3)))
        #print "on_alloc " ,ret
        return ret

    def on_apara(self,node):
        #print "on_apara" , node.query("explist>exp")
        return [self.on_exp(x) for x in node.query("explist>exp")]


def run():
    ast = parse(test)
    parser = MoreParser(ast)
    parser.parse()
    #print parser.global_ns.ns
    inter = Interpreter(ast,parser.global_ns)
    inter.run()
    #print inter.global_ns.ns

if __name__ == '__main__':
    run()
