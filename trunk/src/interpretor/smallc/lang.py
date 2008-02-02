#coding=gbk
'''
Small C 语言只有三种类型。
1. 整形
2. 整形数组
3. 结构体 (Class)
'''
import operator

class Type:
    pass

class Int(Type):

    def __repr__(self):
        return "int"
    __str__ = __repr__

class Array(Type):

    def __init__(self,dim):
        self.dim = dim

    def __eq__(self,rhs):
        return self.dim == rhs.dim

    def __repr__(self):
        return "int" + "[]" * self.dim

    __str__ = __repr__


class Struct(Type):

    def __init__(self,name,members = []):
        self.name = name
        self.members = members

    def add_memeber(self,type,member_name):
        self.members.append((type,member_name))


    def __repr__(self):
        s = "class " + self.name + "{\n";
        for (type,member_name) in self.members:
            s += "\t" + type +" " +  member_name + "\n"
        s += "}\n"
        return s
    __str__ = __repr__

class Entity:

    def __init__(self,type,value):
        self.type = type
        self.value = value

    def value(self):
        return self.value

    def type(self):
        return self.type

    def copy(self):
        return copy.copy(self)

    @staticmethod
    def assign(lhs,rhs):
        pass
        #if lhs.type != rhs.type

