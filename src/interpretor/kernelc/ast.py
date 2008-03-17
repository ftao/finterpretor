class Node:
    def __init__(self,type,children=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = [ ]


    def get_children(self):
        return self.children

