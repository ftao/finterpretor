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

