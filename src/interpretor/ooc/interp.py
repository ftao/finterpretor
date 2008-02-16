#coding=gbk
'''
ooc 语言解释器
工作在抽象语法树上。
'''
import operator
import copy
import sys
import interpretor.ooc.lang as lang
from interpretor.ooc.parse import parse
from interpretor.ooc.lex import test
from interpretor.ooc.ast import Node,Leaf
import interpretor.ooc.error as error

def copy_ns(ns_dict):
    ret = copy.copy(ns_dict)
    for x in ret:
        ret[x] = copy.copy(ns_dict[x])
    return ret


class Namespace:
    '''名字空间。 出现ID时从名字空间中获得对应的对象
    实际上只有一个全局名字空间是这个类的实例。其他都是对应子类的实例。
    '''
    def __init__(self, upper=None):
        self.upper = upper #上级名字空间？
        self.ns = {}
        self.name = "global"

    def get(self, name):
        "取得name 对应的对象"
        if name in self.ns:
            return self.ns[name][0]
        elif self.upper:
            return self.upper.get(name)
        else:
            raise error.NameError(name)

    def __getitem__(self, key):
        return self.get(key)

    def set(self, name, value, decorate = None):
        "将名字加入到名字空间,检查重复定义"
        if name in self.ns:
            raise error.MultipleError(name)
        else:
            self.ns[name] = (value,decorate)

    def __repr__(self):
        return "Namespace %s" %(self.name)

    __str__ = __repr__

class Function(Namespace):
    '''函数。 Namespace 的子类。
    OOC 语言中的函数都属于某一个类
    名字，对应类，返回类型，修饰符(public,static,redef等）
    参数有add_param 方法增加
    TODO: abstract 的问题？
    '''
    def __init__(self,name,cls,ret_type = lang.void, decorate = None):
        self.name = name
        self.params = []
        self.ns = {}
        self.cls = cls
        self.ret_type = ret_type
        self.decorate = decorate
        self.obj = None  #调用函数的对象。

    def add_param(self,name,type):
        '增加一个参数'
        self.params.append(name)
        self.set(name,lang.Object(type))

    def freeze(self):
        '函数定义完成后,冻结这个函数'
        self.ns_org = copy_ns(self.ns)

    def set_param(self, name, value):
        '''函数调用时，设置参数的值'''
        if name not in self.ns:
            raise NameError(name)
        else:
            self.ns[name].op("assign",value)  #注意这里，使用op_assign来设置参数可保证语义正确

    def get(self, name):
        '''取得name 对应的对象
         函数中访问一个名字，来源可能有：
         函数名字空间，实例变量，类变量，类方法，全局名字
        '''
        if name in self.ns:
            return self.ns[name]
        else:
            if self.decorate == "static":#如果调用的静态方法
                #类静态变量，对全局名字空间的访问包含在这个调用中，下同。
                return self.cls.op_get_cls(name)
            else:
                if name == "this":   #对于this 特殊处理
                    return self.obj
                #通过实例可以访问的变量。包括实例变量和类变量
                return self.obj.op("get", name)


    def set(self, name, value):
        '增加名字。函数自己的名字空间中没有修饰符的区别'
        if name in self.ns:
            raise MultipleError(name)
        else:
            self.ns[name] = value

    def call(self,obj,args,inter):
        '在obj 上调用本函数，参数为args, 解释器对象是inter'
        #print "calling func %s in obj %s with args %s" %(self.name,obj,args)
        #下面三个是现场保护， 名字空间字典,调用对象，解释器但前名字空间
        ns_now = self.ns
        #这里的copy_ns 是一个半深半浅的复制
        self.ns = copy_ns(self.ns_org)

        old_obj = self.obj
        self.obj = obj

        old_current = inter.current_ns
        inter.current_ns = self

        for i in range(len(self.params)):
            self.set_param(self.params[i], args[i])
        for st in self.statements:
            ret = inter.on_statement(st)

        #恢复现场
        self.ns = ns_now
        inter.current_ns = old_current
        self.obj = old_obj

        #转换成返回类型
        return ret.op("tcast", self.ret_type)

    def __repr__(self):
        return "Function %s " %self.name

    __str__ = __repr__

#下面是几个内置函数，或者说是操作符。
class PrintFunc(Function):
    def __init__(self):
        self.name = "print"

    def call(self,obj,args,inter):
        for x in args:
            x.op("print")
        return lang.Object(lang.void)

    def __repr__(self):
        return "function %s" %(self.name)

class PrintlnFunc(Function):
    def __init__(self):
        self.name = "println"

    def call(self,obj,args,inter):
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
    def call(self,obj,args,inter):
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
    def call(self,obj,args,inter):
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
        'int': (lang.intType,"builtin"),
        'void': (lang.void,"builtin"),
        'null': (lang.null,"builtin"),
        'print': ((PrintFunc(),None),"builtin"),
        'println': ((PrintlnFunc(),None),"builtin"),
        'read': ((ReadFunc(inputFlags),None),"builtin"),
        'eof': ((EofFunc(inputFlags),None),"builtin")
    }
    return ns


class MoreParser:
    '''在AST 基础上进一步处理，根据声明语句解析类声明'''
    def __init__(self,ast):
        self.ast = ast
        self.global_ns = get_built_in_namespace()
        self.current_ns = self.global_ns

    def parse(self):
        '''walk the ast , build the golbal namespace and classses '''

        #类定义  注意这里分了两步来解析类声明。用来解决嵌套问题。 一个类的成员是另一个尚未定义的类
        for n in self.ast.query("classdecl"):
            name = self.on_token(n.child(2))
            base_cls = None
            decorate = None
            if n.child(3):
                base = self.on_token(n.child(3).child(1))
                base_cls = self.current_ns.get(base)
            if n.child(1):
                decorate = "abstract"
            cls = lang.Class(name, self.global_ns, base_cls, decorate)
            self.global_ns.set(name, cls, decorate)

        for n in self.ast.query("classdecl"):
            name = self.on_token(n.child(2))
            cls = self.global_ns.get(name)
            #常量
            for con in n.query("pos_condecl>condecl>condef"):
                self.on_condef(con, cls)

            for mem in n.query("pos_static>member"):
                self.on_member(mem, cls, "static")

            for mem in n.query("pos_private>member"):
                self.on_member(mem, cls, "private")

            for mem in n.query("pos_public>member"):
                self.on_member(mem, cls, "public")

            for cfdef in n.query("pos_redef>cfdef_list>cfdef"):
                self.on_cfdef(cfdef, cls, "redef")


    def on_member(self,node,cls,decorate):
        for decl in node.query("vdecl>decllist>decl"):
            self.on_decl_inside_class(decl,cls,decorate)
        for afdef in node.query("fdefs>fdef>afdef"):
            self.on_afdef(afdef,cls,decorate)
        for cfdef in node.query("fdefs>fdef>cfdef"):
            self.on_cfdef(cfdef,cls,decorate)


    def on_decl_inside_class(self,node,cls,decorate):
        type = self.on_type(node.child(0))
        for id in node.child(1):
            cls.add_var(self.on_token(id),type,decorate)


    def on_afdef(self,node,cls,decorate):
        "抽象函数声明"
        #TODO Not Finished
        name  = self.on_token(node.child(3))
        fns = Function(name,cls,self.on_type(node.child(2)),decorate)
        fns.argType = []
        cls.add_func(name,fns,decorate)
        for type in node.query("type_list>type"):
            fns.argType.append(self.on_type(type))
        fns.freeze()


    def on_cfdef(self,node,cls,decorate):
        name  = self.on_token(node.child(2).child(0))
        fns = Function(name,cls,self.on_type(node.child(1)),decorate)
        cls.add_func(name,fns,decorate)

        for para in node.query("head>paralist>paradecl"):
            self.on_paradecl(para,fns)
        for decl in node.query("funbody>vdecl>decllist>decl"):#vdecl > decllist > decls
            self.on_decl_in_func(decl,fns)
        fns.statements = node.query("funbody>stlist>st")
        fns.freeze()

    def on_decl_in_func(self,node,ns):
        type = self.on_type(node.child(0))
        for id in node.child(1):
            ns.set(self.on_token(id),lang.Object(type))
    #函数形参定义
    def on_paradecl(self,node,ns):
        type = self.on_type(node.child(0))
        name = self.on_token(node.child(1))
        ns.add_param(name,type)

    def on_type(self,node):
        base = self.on_token(node.child(0))
        base_type = self.current_ns.get(base)
        if not base_type:
            pass # raise Error
        else:
            if len(node) > 1:
                dim = (len(node) - 1)/2
                return lang.Array(base_type, dim)
            else:
                return base_type

    def on_condef(self,node,cls):
        #print node
        name = self.on_token(node.child(0))
        value = self.on_token(node.child(-1))
        if len(node) > 3:
            value = -value
        cls.add_var(name,lang.ConstObject(lang.intType,value),'const') # type use lang.intType

    def on_token(self,node):
        self.current_token = node
        return node.value

class Interpreter:

    def __init__(self,ast,global_ns):
        self.ast = ast
        self.global_ns = global_ns
        self.current_ns = None

    def run(self):
        self.current_ns = self.global_ns
        try:
            main_cls = self.current_ns.get("Main")
            main = main_cls.op_member_cls("main")
            main[0].call(main[1],[],self)
        except Exception,e:
        #except error.LangError,e:
            print "error at line %d near token '%s': %s" %(self.current_token.lineno,self.current_token.value,str(e))
            raise

    def on_statement(self,node):
        node = node.child(0)
        if node.type == "cond":
            return self.on_cond(node)
        elif node.type == "loop":
            return self.on_loop(node)
        elif node.type == "exp":
            return self.on_exp(node)

    def on_cond(self,node):
        #print node
        exp = node.child(2)
        st = node.child(4)
        if self.on_exp(exp):
            return self.on_statement(st)
        elif len(node) > 6:
            return self.on_statement(node.child(6))
        return lang.Object(lang.void)

    def on_loop(self,node):
        #print node
        exp = node.child(2)
        ret = lang.Object(lang.void)
        while self.on_exp(exp):
            if len(node) > 4:
                ret = self.on_statement(node.child(4))
        return ret

    def on_exp(self,node):
        #print node
        if len(node) > 1:
            lhs = self.on_orexp(node.child(0))
            self.on_token(node.child(1))
            rhs = self.on_orexp(node.child(2))
            return lhs.op("assign",rhs)
        else:
            return self.on_orexp(node.child(0))

    def on_orexp(self,node):
        if len(node) > 1:
            lhs = self.on_orexp(node.child(0))
            self.on_token(node.child(1))
            rhs = self.on_andexp(node.child(2))
            return lhs.op("or",rhs)
        else:
            return self.on_andexp(node.child(0))

    def on_andexp(self,node):
        if len(node) > 1:
            lhs = self.on_andexp(node.child(0))
            self.on_token(node.child(1))
            rhs = self.on_relexp(node.child(2))
            return lhs.op("and",rhs)
        else:
            return self.on_relexp(node.child(0))

    def on_relexp(self,node):
        if len(node) > 1:
            lhs = self.on_relexp(node.child(0))
            m = {
             '==':'eq',
             '!=':'ne',
             '<':'lt',
             '>':'gt',
             '<=':'le',
             '>=':'ge'
            }
            relop = m[self.on_token(node.child(1))]
            rhs = self.on_term(node.child(2))

            return lhs.op(relop,rhs)
        else:
            return self.on_term(node.child(0))

    def on_term(self,node):
        if len(node) > 1:
            lhs = self.on_term(node.child(0))
            op = {'+':'add','-':'minus'}[self.on_token(node.child(1).child(0))]
            rhs = self.on_factor(node.child(2))
            return lhs.op(op,rhs)
        else:
            return self.on_factor(node.child(0))

    def on_factor(self,node):
        if len(node) > 1:
            lhs = self.on_factor(node.child(0))
            op =  {'*':'mul','/':'div','%':'mod'}[self.on_token(node.child(1).child(0))]
            rhs = self.on_uniexp(node.child(2))
            return lhs.op(op,rhs)
        else:
            return self.on_uniexp(node.child(0))

    def on_uniexp(self,node):

        if len(node) > 1:
            uniop = {'++':'inc','--':'dec',
                    '-':'minus_','!':'not','chk':'chk'}[self.on_token(node.child(0).child(0))]
            uniexp = self.on_uniexp(node.child(1))
            return uniexp.op(uniop)
        else:
            return self.on_postexp(node.child(0))

    def on_postexp(self,node):

        if len(node) > 1:
            postexp = self.on_postexp(node.child(0))
            postfix = node.child(1).child(0)
            if postfix.type == 'apara':
                func = postexp[0]
                obj = postexp[1]
                if len(postfix) == 2:
                    return func.call(obj,[],self)
                else:
                    return func.call(obj,self.on_apara(postfix),self)
            elif postfix.type =='index':
                return postexp.op("index",self.on_exp(postfix.child(1)))
            elif postfix.type == 'aselect':
                if isinstance(postexp, lang.Object):
                    #这里检测但前所在函数是否是postexp 的类。
                    #如果是,可以访问私有变量
                    #否则，不能访问私有变量
                    if self.current_ns.cls == postexp.type:
                        return postexp.op("member",self.on_token(postfix.child(1)))
                    else:
                        return postexp.op("member_no_private",self.on_token(postfix.child(1)))
                elif isinstance(postexp, lang.Class):
                    return postexp.op_member_cls(self.on_token(postfix.child(1)))
                else:
                    raise error.UnsupportedOPError("member")

            elif postfix.type == 'tcast':
                return postexp.op("tcast",self.on_type(postfix.child(1)))
            if isinstance(postfix,Leaf):
                value = self.on_token(postfix)
                if value == '++':
                    return postexp.op("inc_")
                elif value == '--':
                    return postexp.op("dec_")
        else:
            return self.on_entity(node.child(0))



    def on_type(self,node):
        base = self.on_token(node.child(0))
        base_type = self.current_ns.get(base)
        if len(node) > 1:
            dim = len(node) - 1
            return lang.Array(base_type, dim)
        else:
            return base_type

    def on_entity(self,node):
        entity = node.child(0)
        if entity.type == "cast":
            return self.on_cast(entity)
        elif entity.type == "alloc":
            return self.on_alloc(entity)
        elif isinstance(entity,Leaf):
            entity = self.on_token(entity)
            if isinstance(entity,str):
                #if entity == '?': #input
                #    return self.current_ns.get("read").call([],self)
                #else:
                ret = self.current_ns.get(entity)
                return ret
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
        return ret

    def on_apara(self,node):
        return [self.on_exp(x) for x in node.query("explist>exp")]

    def on_token(self,node):
        self.current_token = node
        return node.value


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
