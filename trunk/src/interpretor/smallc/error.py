#coding=utf8
#$Id$
'''
错误类型和错误报告系统
'''
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

#词法分析错误

#语法分析错误
class ParseError(Exception):

    def __init__(self,token):
        self.token = token

    def __str__(self):
        return "Parser error at line %d token '%s'"  %(self.token.lineno, self.token.value)

#静态语义错误
class StaticSemanticError(LangError):
    '''静态语义错误'''
    pass

class NameError(StaticSemanticError):
    def __init__(self, name):
        self.name = name
        self.msg = "name '%s' is not defined" %(self.name)

class NameReDefineError(StaticSemanticError):
    def __init__(self, name):
        self.name = name
        self.msg = "name '%s' is already defined" %(self.name)

class TypeCheckError(StaticSemanticError):
    def __init__(self, op):
        self.op = op
        self.msg = "type not match for operation '%s'" %(self.op)

class MemberError(StaticSemanticError):
    def __init__(self, type, member):
        self.type = type
        self.member = member
        self.msg = "'%s' dont't have '%s' member" %(self.type.name, self.member)

class ParamCountNotMatchError(StaticSemanticError):
    def __init__(self, expect_count, real_count):
        self.expect_count = expect_count
        self.real_count = real_count
        self.msg = "param count not match , expect %d , got %d" %(self.expect_count, self.real_count)


#运行时错误
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
        return "Except object with type %s , got %s" %(self.lhs,self.rhs)



class UnsupportedOPError(LangError):
    def __init__(self,op):
        self.op = op

    def __str__(self):
        return "Unsupported operation '%s'" %(self.op)

class IndexError(LangError):
    def __init__(self,ind,range):
        self.index = ind
        self.range = range

    def __str__(self):
        return "Index %s out of range [%d,%d)" %(self.index ,self.range[0], self.range[1])


class ChkFailError(LangError):
    def __str__(self):
        return "Chk failed"

class NullError(LangError):
    def __init__(self,obj):
        self.obj = obj

    def __str__(self):
        return "%s is null." %(self.obj)


class EmptyReferenceError(LangError):
    def __init__(self,obj):
        self.obj = obj

    def __str__(self):
        return "%s is empty (hanging reference)." %(self.obj)


class EOFError(LangError):
    def __init__(self):
        pass
    def __str__(self):
        return "EOF Error."