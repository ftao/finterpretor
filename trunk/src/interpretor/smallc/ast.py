
class Node:
    def __init__(self,type,children=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = [ ]

    def getChildren(self):
        return self.children


    def __iter__(self):
        for n in self.getChildren():
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

    def asList(self): # for backwards compatibility
        return self.getChildren()

    def __repr__(self):
        #return "(%s(%s))" %(self.type,repr(self.getChildren()))
        return "".join([str(x) for x in self.get_all_tokens()])

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

def walk(node,process):
    '''walk the ast , and do something to the nodes '''
    process(node)
    for x in node:
        process(x)




