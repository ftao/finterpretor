#coding=gbk
'''
Small C 语言只有三种类型。
1. 整形
2. Void
3. 数组
4. 结构体 （数组）
'''
import operator


class Singleton(type):
    def __call__(cls, *args):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__call__(*args)
        return cls.instance

class Type(object):
    def op_assign(self,lhs,rhs):
        if lhs.type == rhs.type:
            lhs.value = rhs.value
            return lhs
        else:
            pass # Raise Error

    def alloc(self,size):
        pass

class Void(Type):
    pass

class Integer(Type):
    '''Small C 整数类型'''

    def op_print(self,obj):
        print obj.value,

    def op_println(self,obj):
        print obj.value

    def op_or(self,lhs,rhs):
        return Object(Integer(), int(bool(lhs.value or rhs.value)))

    def op_and(self,lhs,rhs):
        return Object(Integer(), int(bool(lhs.value and rhs.value)))

    def op_eq(self,lhs,rhs):
        return Object(Integer(), int(lhs.value == rhs.value))

    def op_ne(self,lhs,rhs):
        return Object(Integer(), int(lhs.value != rhs.value))

    def op_lt(self,lhs,rhs):
        return Object(Integer(), int(lhs.value < rhs.value))

    def op_gt(self,lhs,rhs):
        return Object(Integer(), int(lhs.value > rhs.value))

    def op_le(self,lhs,rhs):
        return Object(Integer(), int(lhs.value <= rhs.value))

    def op_ge(self,lhs,rhs):
        return Object(Integer(), int(lhs.value >= rhs.value))

    def op_add(self,lhs,rhs):
        return Object(Integer(), lhs.value + rhs.value)

    def op_minus(self,lhs,rhs):
        return Object(Integer(), lhs.value - rhs.value)

    def op_mul(self,lhs,rhs):
        return Object(Integer(), lhs.value * rhs.value)

    def op_div(self,lhs,rhs):
        return Object(Integer(), lhs.value / rhs.value)

    def op_mod(self,lhs,rhs):
        return Object(Integer(), lhs.value % rhs.value)

    def op_minus_(self,rhs):
        return Object(Integer(), - rhs.value)

    def op_not(self,rhs):
        return Object(Integer(), int(not rhs.value) )

    def op_inc(self,rhs):
        rhs.value += 1
        return rhs

    def op_dec(self,rhs):
        rhs.value -= 1
        return rhs

    def op_chk(self,rhs):
        pass

    def op_inc_(self,lhs):
        ret = Object(Integer(), lhs.value)
        lhs.value += 1
        return ret

    def op_dec_(self,lhs):
        ret = Object(Integer(), lhs.value)
        lhs.value -= 1
        return ret

    def __repr__(self):
        return "int"

    def __eq__(self,rhs):
        return type(self) == type(rhs)

    __str__ = __repr__

class Array(Type):

    def __init__(self,base,dim = 1):
        if dim > 1:
            self.base = Array(self.base, dim-1)
            dim = 1
        else:
            self.base = base
            self.dim = 1

    def __eq__(self,rhs):
        return type(self) == type(rhs) and self.base == rhs.base and self.dim == rhs.dim

    def __repr__(self):
        pass #return "int" + "[]" * self.dim

    def op_index(self,lhs,rhs):
        if rhs.type != Interger():
            #TODO do something here
            pass
        ind = rhs.value
        if self.dim > 1:
            return Object(Array(self.dim-1), lhs.value[ind])
        else:
            return Object(Integer(), lhs.value[ind])

    def alloc(self,obj,size):
        obj.value = [Object(obj.type.base)] * size

    __str__ = __repr__


class Struct(Type):

    def __init__(self,name,members = []):
        self.name = name
        self.members = members

    def add_member(self,type,member_name):
        self.members.append((type,member_name))

    def op_member(self,lhs,rhs):
        pass

    def __eq__(self,rhs):
        return type(self) == type(rhs) and self.name == rhs.name

    def __repr__(self):
        s = "class " + self.name + "{\n";
        for (type,member_name) in self.members:
            s += "\t" + type +" " +  member_name + "\n"
        s += "}\n"
        return s
    __str__ = __repr__

class Object:

    def __init__(self,type,value = None):
        self.type = type
        self.value = value

    def value(self):
        return self.value

    def type(self):
        return self.type

    def op(self,op,arg = None):
        try:
            func = getattr(self.type,"op_"+op)
            if arg:
                return func(self,arg)
            else:
                return func(self)
        except AttributeError:
            return None

    def alloc(self,size = 1):
        self.type.alloc(self,size)

class ConstObject(Object):

    def op(self,op,arg = None):
        if op == "assign" or op == "inc" or op == "inc_" or op == "dec" or op == "dec_":
            pass # raise Error
        else:
            super(ConstObject, self).op(op,arg)

#    def ops(self,op,arg):
#        if op == '=':
#            return self.type.op_assign(self,arg)
#        elif op == '||':
#            return self.type.op_or(self,arg)
#        elif op == '&&':
#            return self.type.op_and(self,arg)
#        elif op == '==':
#            return self.type.op_eq(self,arg)
#        elif op == '!=':
#            return self.type.op_neq(self,arg)
#        elif op == '<':
#            return self.type.op_lt(self,arg)
#        elif op == '>':
#            return self.type.op_gt(self,arg)
#        elif op == '<=':
#            return self.type.op_le(self,arg)
#        elif op == '>=':
#            return self.type.op_ge(self,arg)
#        elif op == '+':
#            return self.type.op_le(self,arg)
#        elif op == '-':
#            if arg:
#                return self.type.op_minus(self,arg)
#            else:
#                return self.type.op_minus_(self)
#        elif op == '*':
#            return self.type.op_mul(self,arg)
#        elif op == '/':
#            return self.type.op_div(self,arg)
#        elif op == '%':
#            return self.type.op_mod(self,arg)
#        elif op == '!':
#            return self.type.op_not(self)
#        elif op == '++':
#            return self.type.op_not(self)
#        elif op == 'chk':
#            return self.type.op_chk(self)
#        elif op == 'chk':
#            return self.type.op_chk(self)
#        elif op == '[]':
#            return self.type.op_index(self,arg)
#        elif op == '.':
#            return self.type.op_member(self,arg)
