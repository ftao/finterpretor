#coding=gbk
'''
SmallC 语言解释器
工作在抽象语法树上。
SmallC 不允许函数嵌套。
'''
import operator
import interpretor.smallc.lang as lang
import copy

class Namespace:
    def __init__(self, upper = None):
        self.upper = upper
        self.ns = {}

    def get(self, name):
        if name in self.ns:
            return self.ns[nama]
        elif self.upper:
            return self.upper.get(name)

    def __getitem__(self, key):
        return self.get(key)

    def set(self, name, value):
        if name in self.ns:
            pass # raise Error
        else:
            self.ns[name] = value
    def __setitem__(self, key, value):
        self.set(key, value)

class Namespace_:
    def __init__(self,upper = None):
        self.upper = upper
        self.s_const = {}
        self.s_var = {}
        self.s_type = {}
        self.s_function = {}

    def get_any(self,name):
        for type in ("const","var","type","function"):
            if hasattr('s_'+self,type) and name in self.__dict__['s_'+self,type]:
                return self.__dict__['s_'+self,type]
        for type in ("const","var","type","function"):
            return self.uppper.get(type,name)

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

    def set_type(self,name,value):
        self.set("type",name,value)

class Function(Namespace):
    def __init__(self,ret_type = lang.Void(),paras = [],upper):
        self.upper = upper
        self.ns = {}
        self.ret_type = ret_type
        self.params = []
        self.statements = []
        for x in paras:
            self.add_param(x[0],x[1])

    def add_param(self,name,type):
        self.params.append(name)
        self.set(name,lang.Object(type))

    def call(self,args,inter):
        ns_copy = copy.copy(self.ns)
        for i in range(len(self.params)):
            self.set(self.params[i], args[i])
        for st in self.statements:
            ret = inter.on_st(st, self)
        return ret.op("tcast", self.ret_type)

class Function_(Namespace):
    def __init__(self,ret_type = "",paras = "",upper):
        self.s_upper = upper
        #self.consts = {}
        self.s_vars = {}
        #self.types = {}
        #self.functions = {}
        self.s_params = []

        self.s_statements = []

    def add_param(self,name,type):
        self.s_params.append(name)
        self.s_vars[name] = lang.Object(type)




def get_built_in_namespace():
    ns = Namespace()
    ns.s_type = {
        'int':lang.Integer(),
        'void':lang.Void()
    }
    ns.s_function = {
        'print':'print',
        'println':'println'
    }
    return ns


class Parser:
    '''在AST 基础上进一步处理，根据声明语句建立名字空间和函数对象'''
    def __init__(self,ast):
        self.ast = ast
        self.global_ns = get_built_in_namespace()
        self.current_ns = global_ns

    def parse(self):
        '''walk the ast , build the golbal namespace'''

        #类定义
        for n in self.ast.get_by_type("classdecls"):
            name = n.get_by_type("id")[0].value
            struct = lang.Struct(name)
            decls = n.get_by_type("decl")
            for x in decls:
                self.on_decl_inside_class(x,struct)
            self.global_ns.set_type(name, struct)
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

    def on_decl_inside_class(self,node,struct):
        type = self.on_type(node.child(0))
        for n in node.child(1).get_by_type('id'):
            struct.add_member(type,n.value) #None 不够好。 应该用一个未知的变量来处理。

    #函数形参定义
    def on_paradecl(self,node,ns):
        type = self.on_type(node.child(0))
        name = node.child(1).value
        ns.add_param(name,type)

    def on_type(self,node):
        base = node.child(0).value
        base_type = self.current_ns.get_type(base)
        if not base_type:
            pass # raise Error
        else:
            if len(node) > 1:
                dim = len(node) - 1
                return lang.Array(base_type, dim)
            else:
                return base_type

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
            return lhs.op("assign",rhs)
        else:
            return self.on_orexp(node.child(0))

    def on_orexp(self,node):
        if node.child_or_none(1):
            lhs = self.on_orexp(node.child(0))
            rhs = self.on_andexp(node.child(2))
            return lhs.op("or",rhs)
        else:
            return self.on_andexp(node.child(0))

    def on_andexp(self,node):
        if node.child_or_none(1):
            lhs = self.on_andexp(node.child(0))
            rhs = self.on_relexp(node.child(2))
            return lhs.op("and",rhs)
        else:
            return self.on_relexp(node.child(0))

    def on_relexp(self,node):
        if node.child_or_none(1):
            lhs = self.on_relexp(node.child(0))
            rhs = self.on_term(node.child(2))
            relop = node.child(1).child(0).type[:-2]
            return lhs.op(relop,rhs)
        else:
            return self.on_term(node.child(0))

    def on_term(self,node):
        if node.child_or_none(1):
            lhs = self.on_term(node.child(0))
            rhs = self.on_factor(node.child(2))
            op = {'+':'add','-':'minus'}[node.child(1).child(0).value]
            return lhs.op(op,rhs)
        else:
            return self.on_factor(node.child(0))

    def on_factor(self,node):
        if node.child_or_none(1):
            lhs = self.on_factor(node.child(0))
            rhs = self.on_uniexp(node.child(2))
            op =  {'*':'mul','/':'div','%':'mod'}[node.child(1).child(0).value]
            return lhs.op(op,rhs)
        else:
            return self.on_uniexp(node.child(0))

    def on_uniexp(self,node):
        if node.child_or_none(1):
            uniop = {'++':'inc','--':'dec',
                    '-':'minus_','!':'not','chk':'chk'}[node.child(0).child(0).value]
            uniexp = self.on_uniexp(node.child(1))
            return uniexp.op("uniop")
        else:
            return self.on_postexp(node.child(0))

    #TODO error
    def on_postexp(self,node):
        if node.child_or_none(1):
            postexp = self.on_postexp(node.child(0))
            postfix = node.child(1).child(0)
            if isinstance(postfix,Node):
                if postfix.type == 'apara':
                    return postexp.call(self.on_apara(postfix.child(1)),self)
                elif postfix.type =='sub':
                    return postexp.op("index",self.on_sub(postfix.child(1)))
                elif postfix.type == 'aselect':
                    return postexp.op("member",postfix.child(1).value)
                elif postfix.type == 'tcast':
                    return postexp.op("tcast",self.on_type(postfix.child(1)))
            else:
                if postfix.value == '++':
                    return postexp.op("inc_")
                elif postfix.value == '--':
                    return postexp.op("dec_")
        else:
            return self.on_entity(node.child(0))

    def on_sub(self,node):
        return self.on_exp(node.child(1))

    def on_type(self,node):
        base = node.child(0).value
        base_type = self.current_ns.get_type(base)
        if not base_type:
            pass # raise Error
        else:
            if len(node) > 1:
                dim = len(node) - 1
                return lang.Array(base_type, dim)
            else:
                return base_type

    def on_entity(self,node):
        entity = node.child(0)
        if entity.type == "id":
            return self.current_ns.get_any(entity.value)
        elif entity.type == "num":
            return lang.Object(lang.Integer(), entity.value)
        elif entity.type == "cast":
            return self.on_cast(entity)
        elif entity.type == "alloc":
            return self.on_alloc(entity)
        elif entity.type == "?": # input
            inp = raw_input()
            return lang.Object(lang.Integer(), int(inp))

    def on_cast(self,node):
        '''cast 的语义？ 最后一个statement 的值'''
        for x in node.get_by_type("st"):
            ret = self.on_statement(x)
        return ret

    def on_alloc(self,node):
        if len(node) == 2:
            return lang.Object(self.on_type(node.child(1)))
        else:
            ret = lang.Object(lang.Arrray(self.on_type(node.child(1),1)))
            ret.alloc(self.on_exp(node.child(3)))
            return ret

    def on_apara(self,node):
        pass


