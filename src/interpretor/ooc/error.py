#coding=gbk

class LangError(Exception):
    pass

class TCastError(LangError):

    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "Cant't convert from %s to %s" %(self.lhs, self.rhs)

class TypeError(LangError):

    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "Except %s , got %s" %(self.lhs,self.rhs)


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
        return "unsupported operation '%s'" %(self.op)

class IndexError(LangError):
    def __init__(self,ind,range):
        self.index = ind
        self.range = range

    def __str__(self):
        return "index %s out of range %s" %(self.index ,repr(self.range))


class ChkFailError(LangError):
    def __str__(self):
        return "chk failed"

class NullError(LangError):
    def __init__(self,obj):
        self.obj = obj

    def __str__(self):
        return "%s is null." %(self.obj)

class MemberError(LangError):
    def __init__(self,obj,member):
        self.obj = obj
        self.member = member

    def __str__(self):
        return "%s don't have '%s' member ." %(self.obj,self.member)

class UnimplementedMethodError(LangError):
    def __init__(self, method, cls):
        self.method = method
        self.cls = cls

    def __str__(self):
        return "method '%s' of class '%s' is unimplemented (abstract)." %(self.method, self.cls)