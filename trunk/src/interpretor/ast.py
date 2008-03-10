#coding=gbk
class Node:
    def __init__(self,type,children=[],prod = None):
        self.type = type
        self.children = children #filter(lambda child:isinstance(child,Node),children)

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
        '''��ѯ���﷨���� [type|*] {>[type|*])
        eg.  fdef  ����Ϊfdef ���ӽ��
             fdef>vdecl ����Ϊfdef���ӽ�����������Ϊvdecl���ӽ��
             *>exp �ڶ����exp���
             **>exp ��������Ϊexp �Ľ�㡣�����ܲ��)
             ����>?����Ҷ���
             ? ��ʾҶ���
        '''
        ret = []
        qs = q.split(">")
        for child in self.children:
            if child is None:
                continue
            if child.type == qs[0] or qs[0] == '*':
                if len(qs) > 1:
                    ret.extend(child.query(">".join(qs[1:])))
                else:
                    ret.append(child)
            elif qs[0] == '**':
                if len(qs) == 2:
                    if child.type == qs[1]:
                        ret.append(child)
                    ret.extend(child.query(q))
        return ret


    def __repr__(self):
        return " ".join([repr(x) for x in self.query("**>?")])

    __str__ = __repr__





class Leaf(Node):

    def __init__(self,value,lineno,lexpos):
        self.type = "?"
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