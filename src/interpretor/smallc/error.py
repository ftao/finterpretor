#coding=gbk

class LangError(Exception):
    pass

class AssignError(LangError):

    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "Cant't assign from %s to %s" %(self.lhs, self.rhs)

class TCastError(LangError):

    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "Cant't convert from %s to %s" %(self.lhs, self.rhs)

class NameError(LangError):
    def __init__(self,name):
        self.name = name

    def __str__(self):
        return "Undefined name %s" %(self.name)

class MultipleError(LangError):
    def __init__(self,name):
        self.name = name

    def __str__(self):
        return "name %s already defined" %(self.name)

class UnsupportedOPError(LangError):
    def __init__(self,op):
        self.op = op

    def __str__(self):
        return "unsupported operation %s" %(self.op)

