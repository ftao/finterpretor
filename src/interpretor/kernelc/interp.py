#coding=utf8
'''
KernelC 语言解释器
工作在抽象语法树上。

'''
import operator
import sys
import interpretor.smallc.lang as lang
import interpretor.smallc.error as error
from interpretor.smallc.function import Function,get_built_in_ns,copy_ns,set_io
from interpretor.smallc.parse import parse
from interpretor.smallc.lex import test
from interpretor.ast import Node,Leaf


class MoreParser:
    '''在AST 基础上进一步处理，根据声明语句建立名字空间和函数'''
    def __init__(self,ast):
        self.ast = ast
        self.global_ns = get_built_in_ns()
        self.current_ns = self.global_ns

    def parse(self):
        '''walk the ast , build the golbal namespace'''
        #函数
        for n in self.ast.query("fdef"):
            self.on_fdef(n,self.global_ns)

    def on_fdef(self,node,ns):
        '函数定义'
        name  = self.on_token(node.child(1))
        fns = Function(name,self.current_ns)
        ns.set(name,fns)

        fns.statements = node.query("stlist>st")


    def on_token(self,node):
        '终结符'
        self.current_token = node #记录当前终结符。调试用
        return node.value

class Interpreter:

    def __init__(self,ast,global_ns):
        self.ast = ast
        self.global_ns = global_ns
        self.current_ns = None
        self.current_token = None
        self.call_stack = []

    def run(self):
        self.current_ns = self.global_ns

        try:
            self.current_ns.get("main").call([],self)
        except error.LangError,e:
            if self.current_token is None:
                print >>sys.stderr,e
            else:
                print >>sys.stderr, "error at line %d near token '%s': %s" %(self.current_token.lineno,self.current_token.value,str(e))
                print >>sys.stderr, "calling stack "
                for x in self.call_stack:
                    if x[1]:
                        print >>sys.stderr, "call %s at line %s" %(x[0], x[1])
                    else:
                        print >>sys.stderr, "call %s" % (x[0])
        except StandardError,e:
            print >>sys.stderr, "Interpretor inner error "
            raise e

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
        if self.on_exp(exp):
            return self.on_statement(node.child(4))
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
            if lhs:
                return lhs
            self.on_token(node.child(1))
            rhs = self.on_andexp(node.child(2))
            return lhs.op("or",rhs)
        else:
            return self.on_andexp(node.child(0))

    def on_andexp(self,node):
        if len(node) > 1:
            lhs = self.on_andexp(node.child(0))
            if not lhs:
                return lhs
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
                    '-':'minus_','!':'not','chk':'chk','*':'get','@':'print'}[self.on_token(node.child(0).child(0))]
            uniexp = self.on_uniexp(node.child(1))
            return uniexp.op(uniop)
        else:
            return self.on_postexp(node.child(0))

    def on_postexp(self,node):

        if len(node) > 1:
            postexp = self.on_postexp(node.child(0))
            postfix = node.child(1).child(0)
            if isinstance(postfix,Leaf):
                value = self.on_token(postfix)
                if value == '++':
                    return postexp.op("inc_")
                elif value == '--':
                    return postexp.op("dec_")
        else:
            return self.on_entity(node.child(0))


    def on_entity(self,node):
        if len(node) > 1:
            return self.on_func_call(node)
        else:
            entity = node.child(0)
            if entity.type == "cast":
                return self.on_cast(entity)
            elif isinstance(entity,Leaf):
                entity = self.on_token(entity)
                if isinstance(entity,str):
                    if entity == '?': #input
                        return self.current_ns.get("read").call([],self)
                    elif entity == '#':
                        return self.current_ns.get("print").call([],self)
                    else:
                        pass #TODO raise ERROR
                elif isinstance(entity,int):
                    return lang.Object(lang.intType, entity)

    def on_cast(self,node):
        '''cast 的语义？ 最后一个statement 的值'''
        for x in node.query("stlist>st"):
            ret = self.on_statement(x)
        return ret

    def on_func_call(self,node):
        '函数调用?'
        func = self.current_ns.get(self.on_token(node.child(0)))
        ret = None
        for st in func.statements:
            ret = self.on_statement(st)
        return ret

    def on_token(self,node):
        self.current_token = node
        return node.value


def run(data, input_file = sys.stdin, output_file = sys.stdout):
    set_io(input_file, output_file)
    try:
        ast = parse(data)
        parser = MoreParser(ast)
        parser.parse()
        #print parser.global_ns.ns
        inter = Interpreter(ast,parser.global_ns)
        inter.run()
    except error.ParseError,e:
        print >>sys.stderr,e
    #print inter.global_ns.ns

if __name__ == '__main__':
    run(test)
