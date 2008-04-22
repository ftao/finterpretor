#coding=utf8
#$Id$
'''
AST Moudle
抽象语法树模块,提供
  # 节结点
  # 叶结点
  # 子结点查询

'''
class Node:

    def __init__(self, type, children=[], prod = None):
        self.type = type
        self.children = children #filter(lambda child:isinstance(child,Node),children)
        #self.prod = prod #记录下原始的产生式对象，也许会用到。 不对不是一一对应的...

    def getChildren(self):
        return self.children

    def __iter__(self):
        for n in self.children:
            yield n

    def __getitem__(self,ind):
        return self.chilren[ind]

    def __len__(self):
        return len(self.children)

    def child(self,ind):
        return self.children[ind]

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
        if isinstance(self, Leaf) and type == '?':
            return True
        if self.type == type:
            return True
        return False

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



#根据parse.py 文件内容 生成抽象语法树遍历程序
def gen_walker(lang):
    import types
    p = __import__('interpretor.%s.parse' %(lang,), fromlist = ['interpretor' ,lang])
    walker_src= "class BaseASTWalker:\n"
    ldict = p.__dict__
    symbols = [ldict[f] for f in ldict.keys()
       if (type(ldict[f]) in (types.FunctionType, types.MethodType) and ldict[f].__name__[:2] == 'p_'
           and ldict[f].__name__[2:] not in p.ast_ommit)]
    symbols.sort(lambda x,y: cmp(x.func_code.co_firstlineno,y.func_code.co_firstlineno))

    for x in symbols:
            walker_src += '''
    def on_%s(self, node):
        return node.child(0)
''' %(x.__name__[2:])
    return walker_src

if __name__ == "__main__":
    print gen_walker("smallc")