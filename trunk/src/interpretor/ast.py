#coding=utf8
#$Id$
'''
AST Moudle
抽象语法树模块,提供
  # 节结点
  # 叶结点
  # 子/父结点查询
  # 导出成图片
  # 通用遍历算法

  # AST 线性化？
'''
class Node:

    def __init__(self, type, children=[],prod = None):
        self.type = type
        self.children = [x for x in children if x is not None] #filter(lambda child:isinstance(child,Node),children)
        #self.prod = prod #记录下原始的产生式对象，也许会用到。 不对不是一一对应的...
        self._attr = {}
        self.parent = None
        for child in self.children:
            if child is not None:
                child.parent = self

    def getChildren(self):
        return self.children

    def __iter__(self):
        for n in self.children:
            yield n

    def __getitem__(self, ind):
        return self.chilren[ind]

#    def __getattr__(self, attr):
#        #create Getter and Setter methods for node attribute
#        if attr.startswith("set_"):
#            attr_name = attr.split('_')[1]
#            t = lambda x, a=attr_name : self._attr.__setitem__(a, x)
#            self.__setattr__(attr,  t)
#            return t
#        elif attr.startswith("get_"):
#            attr_name = attr.split('_')[1]
#            t = lambda a=attr_name : self._attr.__getitem__(a)
#            self.__setattr__(attr,  t)
#            return t

    def __len__(self):
        return len(self.children)

    def child(self, q):
        if isinstance(q, int):
            return self.children[q]
        elif isinstance(q, str):
            result = self.query(q)
            if len(result) == 1:
                return result[0]

    def ancestor(self, type):
        p = self.parent
        while(p):
            if p.type == type:
                break
            else:
                p = p.parent
        return p

    def query(self,q="*"):
        '''查询的语法如下 [type|*] {>[type|*])
        eg.  fdef  类型为fdef 的子结点
             fdef>vdecl 类型为fdef的子结点下面的类型为vdecl的子结点
             *>exp 第二层的exp结点
             **>exp 所有类型为exp 的结点。（不管层次)
             ××>?所有叶结点
             ? 表示叶结点
        '''
        ret = []
        qs = q.split(">")
        for child in self.children:
            if child is None:
                continue
            if child.is_type_match(qs[0]) or qs[0] == '*':
                if len(qs) > 1:
                    ret.extend(child.query(">".join(qs[1:])))
                else:
                    ret.append(child)
            elif qs[0] == '**':
                if len(qs) == 2:
                    if child.is_type_match(qs[1]):
                        ret.append(child)
                    ret.extend(child.query(q))
        return ret

    def is_type_match(self, type):
        #TODO ? is no longer work , as we do have a ? type
        if isinstance(self, Leaf) and type == '?':
            return True
        if self.type == type:
            return True
        return False


    def set_attr(self, name, value):
        self._attr[name] = value

    def get_attr(self, name):
        return self._attr.get(name, None)


    def get_postion(self):
        lextokens = self.query("**>?")
        return (lextokens[0].lineno, lextokens[-1].lineno)
    def __repr__(self):
        return " ".join([repr(x) for x in self.query("**>?")])

    __str__ = __repr__





class Leaf(Node):

    def __init__(self, type, value, lineno, lexpos):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.lexpos = lexpos
        self.children = []
        self._attr = {}
        self.set_attr('value', self.value)

    def __len__(self):
        return 0

    def query(self,qs):
        return []

    def __repr__(self):
        return str(self.value)

    __str__ = __repr__


def all_to_node(p):
    for i in range(len(p)):
        if p[i] is not None and not isinstance(p[i], Node):
            token = p.slice[i]
            p[i] = Leaf(token.type, token.value, token.lineno, token.lexpos)

#导出成图片
#using pydot and graphviz
try:
    import pydot
    def node_to_graph(node, graph):
        if node is None:
            return None
        parent = pydot.Node(
            id(node)
        )
        if isinstance(node, Leaf):
            parent.set_label('%s' %(str(node.value)))
        else:
            parent.set_label(node.type)
        graph.add_node(parent)
        #print parent.to_string()
        for n in node:
            child = node_to_graph(n, graph)
            if child:
                graph.add_edge(pydot.Edge(parent, child))
        return parent

    def to_graph(root, graph_name):
        graph = pydot.Dot()
        node_to_graph(root, graph)
        #print graph.to_string()
        graph.write_png(graph_name + '.png', prog='dot')

except ImportError:
    def to_graph(root, graph_name):
        print "pydot is not installed.to_graphp will not work"


class BaseASTWalker:
    '''深度优先，后序遍历'''
    def __init__(self, root, action):
        self.root = root
        self.action = action
        self.current_token = None

    def _on_node(self, node):
        '''Proxy Method to walk the tree
        Check if a walk_xxx is define ,if so call it
        otherwise call _walk_node
        '''
        if hasattr(self, 'walk_' + node.type):
            return getattr(self, 'walk_' + node.type)(node)
        else:
            if isinstance(node, Leaf):
                return self._walk_token(node)
            else:
                return self._walk_node(node)

    def _walk_node(self, node):
        self._do_action(node, 'before')
        for x in node:
            self._on_node(x)
        self._do_action(node)

    def _do_action(self, node, when = "on"):

        #when shoub be one of ('before', 'on', 'after')
        assert when in ('before', 'on')
        try:
            action = getattr(
                self.action,
                '%s_%s' %(when,node.type)
            )
            action(node)
        except AttributeError,e:
            if isinstance(node, Leaf) and hasattr(self.action, '_%s_token'%(when,)):
                getattr(self.action, '_%s_token'%(when,))(node)
            else:
                self._default_action(node)

    def _default_action(self, node):
        pass

    def _walk_token(self, node):
        self.current_token = node
        self._do_action(node)
        return node.value

    def run(self):
        return self._on_node(self.root)


class ScopeWalker(BaseASTWalker):
    '''一个考虑作用域的遍历方式'''

    def set_ns(self, ns):
        self.ns = ns

    def get_ns(self):
        return self.ns

    def walk_fdef(self, node):
        old_ns = self.ns
        func_name = node.query("head>id")[0].value
        self.ns = self.ns[func_name]
        self._walk_node(node)
        self.ns = old_ns

#根据parse.py 文件内容 生成抽象语法树遍历程序
def gen_action(lang):
    import types
    p = __import__('interpretor.%s.parse' %(lang,), fromlist = ['interpretor' ,lang])
    walker_src= '''#coding=utf8
# This file is automatically generated. Do not edit.
class BaseASTAction:
'''
    ldict = p.__dict__
    symbols = [ldict[f] for f in ldict.keys()
       if (type(ldict[f]) in (types.FunctionType, types.MethodType) and ldict[f].__name__[:2] == 'p_'
           and ldict[f].__name__[2:] not in p.ast_ommit)]
    symbols.sort(lambda x,y: cmp(x.func_code.co_firstlineno,y.func_code.co_firstlineno))

    for x in symbols:
            walker_src += '''
    def on_%s(self, node):
        pass
''' %(x.__name__[2:])

    walker_src += '''
    def _on_token(self, node):
        pass
'''
    return walker_src

if __name__ == "__main__":
    outf = open("smallc/astaction.py", 'w')
    print >>outf, gen_action("smallc")