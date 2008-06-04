#coding=utf8
#$Id$

'''
SmallC 语言解释器
工作在抽象语法树上。
SmallC 不允许函数嵌套。
'''
import operator
import sys
import interpretor.smallc.lang as lang
import interpretor.smallc.error as error
from interpretor.smallc.function import Function,get_built_in_ns,copy_ns,set_io
from interpretor.smallc.parse import parse
from interpretor.smallc.lex import test
from interpretor.ast import Node,Leaf,BaseASTWalker,BaseAnnotateAction
from interpretor.common import CommonOPAnnotate as OPAnnotate

class MoreParser:
    '''在AST 基础上进一步处理，根据声明语句建立名字空间和函数
    这里很大程度需要计算继承属性。（比如当前的所在的结构体,函数)
    但是这个结果似乎不合适标准在AST 上.
    '''

    def __init__(self,ast):
        self.ast = ast
        self.global_ns = get_built_in_ns()
        self.current_ns = self.global_ns
        self.errors = []

    def add_error(self, e):
        self.errors.append(error.Error(self.current_token.lineno, str(e)))

    def parse(self):
        '''walk the ast , build the golbal namespace'''

        #类定义
        for n in self.ast.query("class_decls>classdecl"):
            name = self.on_token(n.child("id"))
            struct = lang.Struct(name)
            self.global_ns.set(name, struct)


        for n in self.ast.query("class_decls>classdecl"):
            name = self.on_token(n.child("id"))
            struct = self.global_ns.get(name)
            for x in n.query("decllist>decl"):
                self.on_decl_inside_class(x, struct)

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
        '(在函数中的)变量声明'
        type = self.on_type(node.child("type"))
        for id in node.query("idlist>id"):
            try:
                ns.set(id.value,lang.Object(type))
            except error.StaticSemanticError, e:
                self.add_error(e)

    def on_decl_inside_class(self,node,struct):
        '在类中的变量声明'
        type = self.on_type(node.child("type"))
        for id in node.query("idlist>id"):
            struct.add_member(type,id.value)

    def on_paradecl(self,node,ns):
        '函数形参定义'
        type = self.on_type(node.child("type"))
        name = self.on_token(node.child("id"))
        ns.add_param(name,type)

    def on_type(self,node):
        '类型'
        base = self.on_token(node.child("id"))
        try:
            base_type = self.current_ns.get(base)
        except error.StaticSemanticError, e:
            self.add_error(e)
            return None
        if node.dim > 0:
            return lang.Array(base_type, node.dim)
        else:
            return base_type

    def on_condef(self,node,ns):
        '常量定义'
        name = self.on_token(node.child("id"))
        value = self.on_token(node.child("num"))
        if node.child("-"):
            value = -value
        try:
            ns.set(name, lang.ConstObject(lang.intType,value)) # type use lang.intType
        except error.StaticSemanticError, e:
            self.add_error(e)

    def on_fdef(self,node,ns):
        '函数定义'
        name  = self.on_token(node.query("head>id")[0])
        fns = Function(name,self.current_ns)
        fns.ret_type = self.on_type(node.child("type"))
        try:
            ns.set(name,fns)
        except error.StaticSemanticError, e:
            self.add_error(e)
            return None
        for para in node.query("head>paralist>paradecl"):
            self.on_paradecl(para,fns)
        for decl in node.query("funbody>vdecl>decllist>decl"):#vdecl > decllist > decls
            self.on_decl(decl,fns)
        fns.statements = node.query("funbody>stlist>st")
        fns.freeze()  #冻结函数,备份原始的名字空间

    def on_token(self,node):
        '终结符'
        self.current_token = node #记录当前终结符。调试用
        return node.value


class Interpreter:
    '''递归解释器'''
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
            raise

    def on_node(self, node):
        if isinstance(node, Leaf):
            return self.on_token(node)
        else:
            if hasattr(self, 'on_' + node.type):
                return getattr(self, 'on_' + node.type)(node)
            else:
                if len(node) == 1:
                    return self.on_node(node.child(0))
                else:
                    print >>sys.stderr, "not such node ", node.type, node



    def on_statement(self, node):
        return self.on_node(node.child(0))

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
        return self.on_node(node.child(0))

    def on_binexp(self, node):
        lhs = self.on_node(node.child(0))
        self.on_node(node.child(1))
        op_name = node.child(1).get_attr('op_name')
        rhs = self.on_node(node.child(2))
        return lhs.op(op_name, rhs)

    on_assignexp = on_binexp

    def on_orexp(self,node):
        lhs = self.on_node(node.child(0))
        if lhs:
            return lhs
        self.on_node(node.child(1))
        rhs = self.on_node(node.child(2))
        return lhs.op("or",rhs)

    def on_andexp(self,node):
        lhs = self.on_node(node.child(0))
        if not lhs:
            return lhs
        self.on_node(node.child(1))
        rhs = self.on_node(node.child(2))
        return lhs.op("and", rhs)

    def on_uniexp(self,node):
        op_name = node.child(0).get_attr('op_name')
        uniexp = self.on_node(node.child(1))
        return uniexp.op(op_name)

    def on_postexp(self,node):
        return self.on_node(node.child(0)).op(node.child(1).get_attr('op_name'))

    def on_func_call(self, node):
        func = self.on_node(node.child(0))
        args = [self.on_node(x) for x in node.getChildren()[1:]]
        line_no = self.current_token.lineno
        return func.call(args, self, line_no)

    def on_array_index(self, node):
        return self.on_node(node.child(0)).op("index", self.on_node(node.child(1)))

    def on_class_member(self, node):
        return self.on_node(node.child(0)).op("member", self.on_node(node.child(1)))

    def on_type_cast(self, node):
        return self.on_node(node.child(0)).op("tcast", self.on_node(node.child(1)))

    def on_type(self, node):
        base = self.on_node(node.child(0))
        base_type = self.current_ns.get(base)
        if node.dim > 0:
            return lang.Array(base_type, node.dim)
        else:
            return base_type

    def on_entity(self,node):
        entity = node.child(0)
        if entity.type == "cast":
            return self.on_node(entity)
        elif entity.type == "alloc":
            return self.on_node(entity)
        elif isinstance(entity,Leaf):
            entity = self.on_node(entity)
            if isinstance(entity,str):
                if entity == '?': #input
                    return self.current_ns.get("read").call([],self)
                else:
                    return self.current_ns.get(entity)
            elif isinstance(entity,int):
                return lang.Object(lang.intType, entity)

    def on_cast(self,node):
        '''cast 的语义？ 最后一个statement 的值'''
        for x in node.query("stlist>st"):
            ret = self.on_node(x)
        return ret

    def on_alloc(self,node):
        if len(node) == 2:
            ret =  self.on_node(node.child(1)).alloc()
        else:
            ret = self.on_node(node.child(1)).alloc(self.on_node(node.child(3)))
        return ret

    def on_apara(self,node):
        return [self.on_node(x) for x in node.query("explist>exp")]

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


    def on_binexp(self, node):
        if len(node) >1:
            self._do_type_trans(node,
                node.child(1).get_attr('op_name'),
                node.child(0).get_attr('type'),
                node.child(2).get_attr('type')
            )
        else:
            self._copy_from_first_child(node)

    def before_funbody(self, node):
        '''在遍历funcbody 的子节点之前,进去对应的名字空间'''
        func_name = node.prev("head").child("id").value
        self.current_ns = self.current_ns.get(func_name)


    def on_funbody(self, node):
        self.current_ns = self.global_ns

    on_st = BaseAnnotateAction._copy_from_first_child

    def on_cond(self, node):
        node.set_attr(self.annotate_attr_name, lang.void)

    def on_loop(self, node):
        node.set_attr(self.annotate_attr_name, lang.void)

    on_exp = BaseAnnotateAction._copy_from_first_child

    on_assignexp = on_orexp = on_andexp = on_binexp


    def on_uniexp(self, node):
        if len(node) > 1:
            self._do_type_trans(node,
                node.child(0).get_attr('op_name'),
                node.child(1).get_attr('type')
            )
        else:
            self._copy_from_first_child(node)

    def on_postexp(self, node):
        self._do_type_trans(node,
            node.child(1).get_attr('op_name'),
            node.child(0).get_attr('type'),
        )

    def on_func_call(self, node):
        '''函数调用，检查参数类型'''
        #FIXME
        func_name = node.child(0).query('**>?')[0].value
        args = node.getChildren()[1:]
        try:
            func = self.current_ns.get(func_name)
        except error.NameError,e:
            self.add_error(e)
            return None
        # a little trick , not check static sem for built in functions
        if func_name not in ['read', 'eof', 'print', 'println']:
            if len(func.params_type) != len(args):
                self.add_error(error.ParamCountNotMatchError(len(func.params_type), len(args)))
            else:
                for i in range(len(func.params_type)):
                    self._check_type('argument_pass', func.params_type[i], args[i].get_attr('type'))
        node.set_attr('type', func.ret_type)

    def on_array_index(self, node):
        '''数组下标操作'''
        self._do_type_trans(node, 'index', node.child(0).get_attr('type'), node.child(1).get_attr('type'))

    def on_class_member(self, node):
        '''结构体成员获取'''
        self._do_type_trans(node, 'member', node.child(0).get_attr('type'), node.child(1).value)

    def on_type_cast(self, node):
        self._do_type_trans(node, 'tcast', node.child(0).get_attr('type'), node.child(1).get_attr('type'))

    on_entity = BaseAnnotateAction._copy_from_first_child

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
        base = node.child(0).value
        try:
            base_type = self.current_ns.get(base)
        except error.StaticSemanticError, e:
            self.add_error(e)
            return None
        if node.dim > 0:
            node.set_attr('type', lang.Array(base_type, node.dim))
        else:
            node.set_attr('type', base_type)

    def _on_token(self, node):
        if node.type == "num" or node.type == '?':
            node.set_attr('type', lang.intType)
        elif node.type == "id":
            try:
                if node.ancestor("funbody"):
                    v = self.current_ns.get(node.value)
                    if isinstance(v, lang.Object):
                        node.set_attr('type', v.type)
            except error.NameError, e :
                pass
                #self.add_error(e)
        self.current_token = node


def run(data, input_file = sys.stdin, output_file = sys.stdout):
    set_io(input_file, output_file)
    try:
        ast = parse(data)
        do_op_annotate(ast)
        global_ns = do_namespace_parse(ast)
        if global_ns:
            if check_static_semtanic(ast, global_ns):
                inter = Interpreter(ast, global_ns)
                inter.run()
    except error.ParseError,e:
        print >>sys.stderr,e
    #print inter.global_ns.ns

def test_OPAnnotate(data):
    ast = parse(data)
    annotate_action = OPAnnotate()
    ast_walker = BaseASTWalker(ast, annotate_action)
    ast_walker.run()
    for x in ast.query('**>?'):
        print x._attr

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
        for e in check_action.errors:
            print >>sys.stderr, e
        return False
    else:
        return True


if __name__ == '__main__':
    #test_OPAnnotate(test)
    run(test)
