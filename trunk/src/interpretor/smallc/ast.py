#coding=gbk
class Node:
    def __init__(self,type,children=[],prod = None):
        self.type = type
        self.children = filter(lambda child:isinstance(child,Node),children)


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

    def query(self,type = "lextoken"):
        ret = []
        for x in self.children:
            if isinstance(x,Node):
                if x.type == type:
                    ret.append(x)
            else:
                if type == "lextoken":
                    ret.append(x)
        return ret

    def query_(self,q="*"):
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
            if isinstance(child,Node):
                if child.type == qs[0] or qs[0] == '*':
                    if len(qs) > 1:
                        ret.extend(child.query(">".join(qs[1:])))
                    else:
                        ret.append(child)
                elif qs[0] == '**':
                    if len(qs) == 2:
                        if child.type == qs[1]:
                            ret.append(child)
                        ret.extend(child.query(qs))
            elif qs[0] == '?':
                ret.append(child)
        return ret


    def __repr__(self):
        return " ".join([str(x) for x in self.query("**>?")])

    __str__ = __repr__

    def get_all_tokens(self):
        ret = []
        for x in self.getChildren():
            if isinstance(x,Node):
                ret.extend(x.get_all_tokens())
            else:
                ret.append(x)
        return ret

    def get_by_type(self,type,only_first_level = True):
        ret = []
        for x in filter(lambda x : x and isinstance(x,Node), self.getChildren()):
            if x.type == type:
                ret.append(x)
                if not only_first_level:
                    ret.extend(x.get_by_type(type,only_first_level))
            else:
                ret.extend(x.get_by_type(type,only_first_level))
        return ret


class Leaf(Node):

    def __init__(self,value,lineno,lexpos):
        self.type = "lextoken"
        self.value = value
        self.lineno = lineno
        self.lexpos = lexpos

