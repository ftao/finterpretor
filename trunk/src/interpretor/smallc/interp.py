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
from interpretor.smallc.astaction import BaseASTAction
from interpretor.ast import Node,Leaf,BaseASTWalker,ScopeWalker


class MoreParser:
    '''在AST 基础上进一步处理，根据声明语句建立名字空间和函数'''
    def __init__(self,ast):
        self.ast = ast
        self.global_ns = get_built_in_ns()
        self.current_ns = self.global_ns

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
            ns.set(id.value,lang.Object(type))

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
        '常量定义'
        name = self.on_token(node.child("id"))
        value = self.on_token(node.child("num"))
        if node.child("-"):
            value = -value
        ns.set(name,lang.ConstObject(lang.intType,value)) # type use lang.intType

    def on_fdef(self,node,ns):
        '函数定义'
        name  = self.on_token(node.query("head>id")[0])
        fns = Function(name,self.current_ns)
        fns.ret_type = self.on_type(node.child("type"))
        ns.set(name,fns)

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
        #except StandardError,e:
        #    print >>sys.stderr, "Interpretor inner error "
        #    raise e

    def on_node(self, node):
        if isinstance(node, Node):
            if hasattr(self, 'on_' + node.type):
                return getattr(self, 'on_' + node.type)(node)
            else:
                pass #should we report error here ?
        else:
            return self.on_token(node)

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
                line_no = self.current_token.lineno
                ret = None
                if len(postfix) == 2:
                    ret = postexp.call([],self,line_no)
                else:
                    ret = postexp.call(self.on_apara(postfix),self,line_no)
                self.on_token(postfix.child(-1))# read the ')', to set the current_token right
                return ret
            elif postfix.type =='sub':
                return postexp.op("index",self.on_exp(postfix.child(1)))
            elif postfix.type == 'aselect':
                return postexp.op("member",self.on_token(postfix.child(1)))
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
                if entity == '?': #input
                    return self.current_ns.get("read").call([],self)
                else:
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
        return ret

    def on_apara(self,node):
        return [self.on_exp(x) for x in node.query("explist>exp")]

    def on_token(self,node):
        self.current_token = node
        return node.value

class OPAnnotate(BaseASTAction):
    '''标注操作符类型
    将 + => 'add' , '-' => 'sub' 等等
    '''
    op_map = {
        '='  : 'assign',
        '&&' : 'and',
        '||' : 'or',
        '==' : 'eq',
        '!=' : 'ne',
        '<'  : 'lt',
        '>'  : 'gt',
        '<=' : 'le',
        '>=' : 'ge',
        '+'  : 'add',
        '-'  : 'minus',
        '*'  : 'mul',
        '/'  : 'div',
        '%'  : 'mod',
        '++' : 'inc',
        '--' : 'dec',
        #'-'  : 'minus_',
        '!'  : 'not',
        'chk': 'chk',
        #'++' : 'inc_',
        #'--' : 'dec_',
    }

    multi_op = ('-', '++', '--')

    #加了个_ 只是为了跟可能出现的on_token区分
    def _on_token(self, node):
        if node.value not in OPAnnotate.op_map:
            return
        op_name = OPAnnotate.op_map[node.value]
        if node.value in OPAnnotate.multi_op:
            if node.value == '-' and node.parent.type == 'uniexp':
                op_name = op_name + '_'
            elif (node.value == '++' or node.value == '--') and node.parent.type == 'postexp':
                op_name = op_name + '_'
        node.set_attr('op_name', op_name)

    def _as_first_child(self, node):
        node.set_attr('op_name', node.child(0).attr('op_name'))

    on_orexp = on_andop = on_relop = on_addop = on_multop = on_uniop = _as_first_child

class StaticTypeChecker(BaseASTAction):
    '''
    静态类型检查
    1.函数不需要执行,只需要返回类型
    2.表达式也只需要返回类型.
    怎样表达运算符对类型的匹配？
    规则定义在哪里呢？
    '''

    #正在标注的属性的名字
    annotate_attr_name = 'type'

    def set_walker(self, walker):
        self.walker = walker #反向应用,遍历器

    def _check_type(self, op, *operands):
        is_type_match = lang.type_constraint.check(
            op,
            *operands
        )
        if not is_type_match:
            print >>sys.stderr,"line ", str(self.current_token.lineno), "type not match for operation " , op
        return is_type_match

    def _check_bin_op(self, node):
        if len(node) >1:
            return self._check_type(node.child(1).get_attr('op_name'), node.child(0).get_attr('type'), node.child(2).get_attr('type'))
        return True

    def _on_bin_exp(self, node):
        self._check_bin_op(node)
        self._copy_from_first_child(node)

    def _copy_from_child(self, node, index):
        node.set_attr(self.annotate_attr_name , node.child(index).get_attr(self.annotate_attr_name))

    def _copy_from_first_child(self, node):
        self._copy_from_child(node, 0)

    on_st = _copy_from_first_child

    def on_cond(self, node):
        node.set_attr(self.annotate_attr_name, lang.void)

    def on_loop(self, node):
        node.set_attr(self.annotate_attr_name, lang.void)

    on_exp = on_orexp = on_andexp = _on_bin_exp

    on_relexp = on_term = on_factor = _on_bin_exp


    def on_uniexp(self, node):
        if len(node) > 1:
            op_name = node.child(0).get_attr('op_name')
            if self._check_type(op_name, node.child(1).get_attr('type')):
                if op_name == 'chk':
                    node.attr('type', lang.void)
                else:
                    self._copy_from_child(node, 1)
        else:
            self._copy_from_first_child(node)


    def on_postexp(self, node):
        #TODO really ugly , need clean up
        postexp = node.child(0)
        if len(node) > 1:
            postfix = node.child(1).child(0)
            if postfix.type == 'apara':
                self._on_postexp_func_call(postexp, postfix)
            elif postfix.type =='sub':
                self._on_postexp_array_index(postexp, postfix)
            elif postfix.type == 'aselect':
                self._on_postexp_member(postexp, postfix)
            elif postfix.type == 'tcast':
                self._on_postexp_tcast(postexp, postfix)
            elif isinstance(postfix,Leaf): # '++' or '--'
                if self._check_type('op_name', postexp.get_attr('type')):
                    node.set_attr('type', postexp.get_attr('type'))
        else:
            self._copy_from_first_child(node)

    ## 这个辅助函数， 在AST不存在对应类型的节点
    def _on_postexp_func_call(self, postexp, postfix):
        '''函数调用，检查参数类型'''
        func_name = postexp.query("**>?")[0].value
        func = self.walker.get_ns().get(func_name)
        args = postfix.query("explist>exp")
        if self._check_type('argument_pass', func.params_type, [a.get_attr('type') for a in args]):
            node.set_attr('type', func.ret_type)

    def _on_postexp_array_index(self, postexp, postfix):
        '''数组下标操作'''
        postexp = node.child(0)
        if self._check_type('index', postexp.get_attr('type'), postfix.child(1).get_attr('type')):
            node.set_attr('type', postexp.get_attr('type').base)

    def _on_postexp_member(self, postexp, postfix):
        '''结构体成员获取'''
        member = postfix.child(1).value
        if self._check_type('member', postexp.get_attr('type'), member):
            node.set_attr('type', postexp.get_attr('type').members[member])

    def _on_postexp_tcast(self, postexp, postfix):
        if self._check_type('tcast', node.child(0).get_attr('type'), postfix.child(1).get_attr('type')):
            node.set_attr('type', postfix.child(1).get_attr('type'))


    on_entity = _copy_from_first_child

    def on_cast(self, node):
        node.attr('type', node.child('stlist').attr('type'))

    def on_stlist(self, node):
        node.attr('type', node[-1].attr('type'))

    def on_alloc(self,node):
        if node.query('['):
            node.attr('type', lang.Array(node.child("type").attr('type')))
        else:
            node.attr('type', node.child("type").attr('type'))

    def on_type(self, node):
        if node.query('['):
            node.attr('type', lang.Array(node.child("type").attr('type')))
        else:
            try:
                node.attr('type', self.walker.get_ns().get(node.child(0).value)) #type : id
            except error.NameError:
                print >>sys.stderr, "bad name , type if not defined"

    def _on_token(self, node):
        if node.type == "num" or node.type == '?':
            node.attr('type', lang.intType)
        elif node.type == "id":
            try:
                #in_func = node.ancestor("fdef")
                #func_name = in_func.query("head>id")[0]
                #func_ns =  self.ns.get(func_name.value)
                #v = self.ns.get(node.value)
                v = self.walker.get_ns().get(node.value)
                if isinstance(v, lang.Object):
                    node.attr('type', v.type)
            except error.NameError:
                print >>sys.stderr, "bad name ", node

        self.current_token = node


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

def test_OPAnnotate(data):
    ast = parse(data)
    annotate_action = OPAnnotate()
    ast_walker = BaseASTWalker(ast, annotate_action)
    ast_walker.run()
    for x in ast.query('**>?'):
        print x._attr

def test_static_checker(data):
    ast = parse(data)
    annotate_action = OPAnnotate()
    ast_walker = BaseASTWalker(ast, annotate_action)
    ast_walker.run()

    parser = MoreParser(ast)
    parser.parse()

    check_action = StaticTypeChecker()
    walker2 = ScopeWalker(ast, check_action)
    walker2.set_ns(parser.global_ns)

    check_action.walker = walker2
    walker2.run()

if __name__ == '__main__':
    #test_OPAnnotate(test)
    test_static_checker(test)
    #run(test)
