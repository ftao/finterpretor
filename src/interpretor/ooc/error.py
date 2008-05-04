#coding=utf8
#$Id$

class Error(Exception):

    error_type = "error" #can be error, warning , notice

    def __init__(self, lineno, msg):
        self.lineno = lineno
        self.msg = msg

    def __str__(self):
        return "line %s: %s: %s" %(self.lineno, self.error_type, self.msg)

class LangError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

    __repr__ = __str__

#静态语义错误
class StaticSemanticError(LangError):
    '''静态语义错误'''
    pass


class NameError(StaticSemanticError):
    '名字未定义错误'
    def __init__(self, name):
        self.name = name
        self.msg = "name '%s' is not defined" %(self.name)

class NameReDefineError(StaticSemanticError):
    '名字重定义错误'
    def __init__(self, name):
        self.name = name
        self.msg = "name '%s' is already defined" %(self.name)

class TypeCheckError(StaticSemanticError):
    '''类型匹配错误'''
    def __init__(self, op):
        self.op = op
        self.msg = "type not match for operation '%s'" %(self.op)

class MemberError(StaticSemanticError):
    '''对象成员错误'''
    def __init__(self, type, member):
        self.type = type
        self.member = member
        self.msg = "'%s' dont't have '%s' member" %(self.type.name, self.member)

class NoPrivateMemberError(StaticSemanticError):
    '''对象公共成员错误'''
    def __init__(self, type, member):
        self.type = type
        self.member = member
        self.msg = "'%s' dont't have '%s' member" %(self.type.name, self.member)

class ClsMmeberError(StaticSemanticError):
    '''类成员错误'''
    def __init__(self, type, member):
        self.type = type
        self.member = member
        self.msg = "'%s' dont't have '%s' class member" %(self.type.name, self.member)


class ParamCountNotMatchError(StaticSemanticError):
    def __init__(self, expect_count, real_count):
        self.expect_count = expect_count
        self.real_count = real_count
        self.msg = "param count not match , expect %d , got %d" %(self.expect_count, self.real_count)



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