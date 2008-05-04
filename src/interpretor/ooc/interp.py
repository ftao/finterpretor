#coding=utf8
#$Id$

'''
ooc 语言解释器
工作在抽象语法树上。
'''
import operator
import copy
import sys
import interpretor.ooc.lang as lang
from interpretor.ooc.parse import parse
from interpretor.ooc.function import Function,AbstractFunction,get_built_in_ns,copy_ns,set_io
from interpretor.ooc.lex import test
import interpretor.ooc.error as error
from interpretor.ast import Node,Leaf,BaseASTWalker,BaseAnnotateAction
from interpretor.common import CommonOPAnnotate as OPAnnotate




class MoreParser:
    '''在AST 基础上进一步处理，根据声明语句解析类声明'''
    def __init__(self,ast):
        self.ast = ast
        self.global_ns = get_built_in_ns()
        self.current_ns = self.global_ns
        self.errors = []

    def add_error(self, e):
        self.errors.append(error.Error(self.current_token.lineno, str(e)))

    def parse(self):
        '''walk the ast , build the golbal namespace and classses '''

        #类定义  注意这里分了两步来解析类声明。用来解决嵌套问题。 一个类的成员是另一个尚未定义的类
        for n in self.ast.query("classdecl"):
            name = self.on_token(n.child('id'))
            base_cls = None
            decorate = None
            if n.child('pos_superclass'):
                base = self.on_token(n.child('pos_superclass').child(1))
                base_cls = self.current_ns.get(base)
            if n.child('pos_abstract'):
                decorate = "abstract"
            cls = lang.Class(name, self.global_ns, base_cls, decorate)
            self.global_ns.set(name, cls, decorate)

        for n in self.ast.query("classdecl"):
            name = self.on_token(n.child('id'))
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
        name  = self.on_token(node.child(3))
        fns = AbstractFunction(name,cls,self.on_type(node.child(2)),decorate)
        cls.add_func(name,fns,decorate)
        for type in node.query("type_list>type"):
            fns.params.append(self.on_type(type))


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
        self.call_stack = []
        self.current_token = None

    def run(self):
        self.current_ns = self.global_ns
        try:
            main_cls = self.current_ns.get("Main")
            main = main_cls.op_member_cls("main")
            main[0].call(main[1],[],self)
        #except Exception,e:
        except error.LangError,e:
            if self.current_token is None:
                print >>sys.stderr,e
            else:
                print >>sys.stderr,"error at line %d near token '%s': %s" %(
                        self.current_token.lineno,
                        self.current_token.value,
                        str(e)
                    )
                print >>sys.stderr, "calling stack "
                for x in self.call_stack:
                    if x[1]:
                        print >>sys.stderr, "call %s at line %s" %(x[0], x[1])
                    else:
                        print >>sys.stderr, "call %s" % (x[0])
        #except StandardError,e:
        #    print >>sys.stderr, "Interpretor inner error "
        #    raise e


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
        #短路计算
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
            relop = m[self.on_token(node.child(1).child(0))]
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
                line_no = self.current_token.lineno
                if len(postfix) == 2:
                    ret =  func.call(obj,[],self,line_no)
                else:
                    ret =  func.call(obj,self.on_apara(postfix),self,line_no)
                # read the ')', to set the current_token right
                self.on_token(postfix.child(-1))
                return ret
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
            dim = (len(node) - 1)/2
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
        #print node.child(1)
        #print self.on_type(node.child(1))
        if len(node) == 2:
            ret =  self.on_type(node.child(1)).alloc()
        else:
            ret = self.on_type(node.child(1)).alloc(self.on_exp(node.child(3)))
        #print "on alloc ",ret
        return ret

    def on_apara(self,node):
        return [self.on_exp(x) for x in node.query("explist>exp")]

    def on_token(self,node):
        self.current_token = node
        return node.value

class StaticTypeChecker(BaseAnnotateAction):
    '''静态类型检查和计算'''
    #正在标注的属性的名字
    annotate_attr_name = 'type'

    def __init__(self, ns):
        self.global_ns = ns
        self.current_ns = ns
        self.errors = []

    def add_error(self, e):
        #print "add error " , e
        #raise
        self.errors.append(error.Error(self.current_token.lineno, str(e)))

    def _do_type_trans(self, node, op, *operands):
        node.set_attr(self.annotate_attr_name, self._check_type(op, *operands))

    def _check_type(self, op, *operands):
        main_type = operands[0]
        if len(operands) > 1:
            arg = operands[1]
        else:
            arg = None
        is_type_match = lang.do_type_trans(main_type, op, arg)
        if not is_type_match:
            if op =='member':
                self.add_error(error.MemberError(operands[0], operands[1]))
            else:
                self.add_error(error.TypeCheckError(op))
        return is_type_match


    def _on_bin_exp(self, node):
        if len(node) >1:
            self._do_type_trans(node,
                node.child(1).get_attr('op_name'),
                node.child(0).get_attr('type'),
                node.child(2).get_attr('type')
            )
        else:
            self._copy_from_first_child(node)

    def before_classdecl(self, node):
        class_name = node.child('id').value
        self.current_class = self.global_ns.get(class_name)
        #print "enter class" , self.current_class

    def on_classdecl(self, node):
        self.current_class = None

    def before_funbody(self, node):
        '''在遍历funcbody 的子节点之前,进去对应的名字空间'''
        func_name = node.prev("head").child("id").value
        #print "enter func " , func_name
        self.current_ns = self.current_class.get_cls_member(func_name)
        if self.current_ns.decorate != "static":
            self.current_ns.obj = self.current_class.alloc_one()
        #print self.current_ns

    def on_funbody(self, node):
        self.current_ns = self.global_ns


    on_st = BaseAnnotateAction._copy_from_first_child

    def on_cond(self, node):
        node.set_attr(self.annotate_attr_name, lang.void)

    def on_loop(self, node):
        node.set_attr(self.annotate_attr_name, lang.void)

    on_exp = on_orexp = on_andexp = _on_bin_exp

    on_relexp = on_term = on_factor = _on_bin_exp


    def on_uniexp(self, node):
        if len(node) > 1:
            self._do_type_trans(node,
                node.child(0).get_attr('op_name'),
                node.child(1).get_attr('type')
            )
        else:
            self._copy_from_first_child(node)

    def on_postexp(self, node):
        postexp = node.child(0)
        if len(node) > 1:
            postfix = node.child(1).child(0)
            if isinstance(postfix,Leaf): # '++' or '--'
                self._do_type_trans(node, postfix.get_attr('op_name'),postexp.get_attr('type'))
            else:#对应不同情况调用下面的辅助函数
                getattr(self, "_on_postexp_" + postfix.type)(node)
        else:
            self._copy_from_first_child(node)
        node.set_attr('id_type', node.child(0).get_attr('id_type'))

    ## 这些辅助函数， 在AST不存在对应类型的节点
    def _on_postexp_apara(self, node):
        '''函数调用，检查参数类型'''
        #print "_on_postexp_apara", node
        postexp = node.child(0)
        postfix = node.child(1).child(0)

        func = postexp.get_attr('type')
        #print "function call " , func
        args = postfix.query("explist>exp")

        if len(func.params_type) != len(args):
            self.add_error(error.ParamCountNotMatchError(len(func.params_type), len(args)))
        else:
            for i in range(len(func.params_type)):
                self._check_type('argument_pass', func.params_type[i], args[i].get_attr('type'))
            node.set_attr('type', func.ret_type)

    def _on_postexp_index(self, node):
        '''数组下标操作'''
        postexp = node.child(0)
        postfix = node.child(1).child(0)
        self._do_type_trans(node, 'index', postexp.get_attr('type'), postfix.child(1).get_attr('type'))

    def _on_postexp_aselect(self, node):
        '''类成员成员获取'''
        postexp = node.child(0)
        postfix = node.child(1).child(0)
        member = postfix.child(1).value
        #print "get member %s from %s" %(member, str(postexp))
        #print postexp._attr
        op_name = None
        if postexp.get_attr('id_type') == 'obj':
            #这里检测但前所在函数是否是postexp 的类。
            #如果是,可以访问私有变量
            #否则，不能访问私有变量
            if self.current_ns.cls == postexp.get_attr('type'):
                op_name = "member"
            else:
                op_name = "member_no_private"
        elif postexp.get_attr('id_type') == 'class':
            op_name = "member_cls"
        if op_name:
           self._do_type_trans(node, op_name, postexp.get_attr('type'), member)

    def _on_postexp_tcast(self, node):
        postexp = node.child(0)
        postfix = node.child(1).child(0)
        self._do_type_trans(node, 'tcast', postexp.get_attr('type'),  postfix.child(1).get_attr('type'))

    def on_entity(self, node):
        node.set_attr('type', node.child(0).get_attr('type'))
        node.set_attr('id_type', node.child(0).get_attr('id_type'))
        #BaseAnnotateAction._copy_from_first_child

    def on_cast(self, node):
        node.set_attr('type', node.child('stlist').get_attr('type'))

    def on_stlist(self, node):
        node.set_attr('type', node.query("st")[-1].get_attr('type'))

    def on_alloc(self,node):
        if node.query('['):
            node.set_attr('type', lang.Array(node.child("type").get_attr('type')))
        else:
            node.set_attr('type', node.child("type").get_attr('type'))

    def on_type(self, node):
        if node.query('['):
            node.set_attr('type', lang.Array(node.child("type").get_attr('type')))
            node.set_attr('id_type', 'class')
        else:
            try:
                node.set_attr('type', self.current_ns.get(node.child(0).value)) #type : id
                node.set_attr('id_type', 'class')
            except error.NameError, e :
                self.add_error(e)

    def _on_token(self, node):
        if node.type == "num" or node.type == '?':
            node.set_attr('type', lang.intType)
        elif node.type == "id":
            try:
                #在函数体里面，并且不是 a.b 这个语法的情况下
                if node.ancestor("funbody") and not node.ancestor("aselect"):
                    v = self.current_ns.get(node.value)
                    #print v
                    if isinstance(v, lang.Object):
                        node.set_attr('type', v.type)
                        node.set_attr('id_type', 'obj')
                    elif isinstance(v, (list,tuple)) and isinstance(v[0], Function):
                        #print "get function " , v[0]
                        node.set_attr('type', v[0])
                        node.set_attr('id_type', 'func')
                    elif isinstance(v, lang.RootClass):
                        node.set_attr('type', v)
                        node.set_attr('id_type', 'class')
            except error.NameError, e :
                self.add_error(e)
        self.current_token = node


def do_op_annotate(ast):
    annotate_action = OPAnnotate()
    ast_walker = BaseASTWalker(ast, annotate_action)
    ast_walker.run()
    return ast

def do_namespace_parse(ast):
    parser = MoreParser(ast)
    parser.parse()
    if len(parser.errors) > 0:
        for x in parser.errors:
            print >>sys.stderr, x
        return None
    return parser.global_ns

def check_static_semtanic(ast, global_ns):
    check_action = StaticTypeChecker(global_ns)
    walker2 = BaseASTWalker(ast, check_action)
    walker2.run()
    if len(check_action.errors) > 0:
        print >>sys.stderr, "found error ", len(check_action.errors)
        for e in check_action.errors:
            print >>sys.stderr, e
        return False
    else:
        return True

def run(data, input_file = sys.stdin, output_file = sys.stdout):
    set_io(input_file, output_file)
    ast = parse(data)
    parser = MoreParser(ast)
    parser.parse()
    #print parser.global_ns.ns
    inter = Interpreter(ast,parser.global_ns)
    inter.run()
    #print inter.global_ns.ns

def run2(data, input_file = sys.stdin, output_file = sys.stdout):
    set_io(input_file, output_file)
    #try:
    ast = parse(data)
    do_op_annotate(ast)
    global_ns = do_namespace_parse(ast)
    if global_ns:
        if check_static_semtanic(ast, global_ns):
            inter = Interpreter(ast, global_ns)
            inter.run()
    #except error.LangError,e:
    #    print >>sys.stderr,e

if __name__ == '__main__':
    test = open('../../test/ooc/static_sem_test.ooc').read()
    run2(test)
