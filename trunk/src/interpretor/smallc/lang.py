#coding=gbk
'''
Small C 语言只有三种类型。
1. 整形
2. Void
3. 数组
4. 结构体 （数组）
'''
import operator
import sys
from interpretor.smallc.error import *

#class Singleton(type):
#    def __call__(cls, *args):
#        if not hasattr(cls, 'instance'):
#            cls.instance = super(Singleton, cls).__call__(*args)
#        return cls.instance

class Type:
    def __init__(self):
        self.name = "type"

    def op_assign(self,lhs,rhs):
        #print "doing assign from %s = %s" %(lhs,rhs)
        if lhs.type == rhs.type or rhs.type == nullType:
            lhs.value = rhs.value
            return lhs
        else:
            raise AssignError(lhs.type,rhs.type)

    def op_eq(self,lhs,rhs):
        return Object(Integer(), int(lhs.value == rhs.value))

    def op_ne(self,lhs,rhs):
        return Object(Integer(), int(lhs.value != rhs.value))

    def alloc(self,size):
        pass

    def op_tcast(self,obj,type):
        #print " tcast %s --> %s" %(obj.type , type)

        if obj.type == type:
            ret = obj
        else:
            ret = Object(type) # TODO raise error ?
        return ret

    def __repr__(self):
        return "<SmallC Type %s>" %self.name

    __str__ = __repr__


class Void(Type):
    def __init__(self):
        self.name = "void"


class Integer(Type):
    '''Small C 整数类型'''

    def __init__(self):
        self.name = "int"

    def init(self,obj,value):
        if value is None or not isinstance(value,int):
            obj.value = 0
        else:
            obj.value = value

    def op_print(self,obj):
        #print "op_print",obj
        sys.stderr.write(str(obj.value) + " ")
        #print obj.value,

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

    def __eq__(self,rhs):
        return type(self) == type(rhs)



class Array(Type):

    def __init__(self,base,dim = 1):
        if dim > 1:
            self.base = Array(base, dim-1)
        else:
            self.base = base
        self.dim = 1
        self.name = self.base.name + "[]" * self.dim

    def __eq__(self,rhs):
        return type(self) == type(rhs) and self.base == rhs.base and self.dim == rhs.dim

#    def op_tcast(self,lhs,rhs):
#        if lhs.type == rhs:
#            return lhs
#        elif rhs.type == NullType():
#            return Object(NullType())

    def init(self,obj,value):
        if value is None or not isinstance(value,list):
            obj.value = []
        else:
            obj.value = value

    def op_assign(self,lhs,rhs):
        if lhs.type == rhs.type:
            lhs.value = rhs.value
        elif rhs.type == NullType():
            lhs.value = []
        return lhs

    def op_index(self,lhs,rhs):
        if rhs.type != Integer():
            #TODO do something here
            pass
        ind = rhs.value
        #print "op_index " ,lhs.value , ind
        return lhs.value[ind]


    def alloc(self,obj,size):
        obj.value = [Object(obj.type.base) for i in range(size.value)]
        #[Object(obj.type.base)] * size.value




class Struct(Type):

    def __init__(self,name):
        self.name = name
        self.members = {}

    def init(self,obj,value):
        if value is None or value is undefined:
            obj.value = {}
        else:
            obj.value = value
        for name in self.members:
            if name not in obj.value:
                obj.value[name] = undefined

    def add_member(self,type,member_name):
        self.members[member_name] = type

    def op_member(self,lhs,rhs):
        if rhs in self.members:
            if lhs.value[rhs] is undefined:
                lhs.value[rhs] = Object(self.members[rhs])
            #print "get member " , lhs.value[rhs]
            return lhs.value[rhs]
        else:
            print "%s Object dont't has '%s' member" %(self.name, rhs)

    def __repr__(self):
        ret = "<SmallC Type %s{" %self.name
        ret += ",".join(["%s:%s" %(x,self.members[x].name) for x in self.members])
        ret += "}>"
        return ret

    def __eq__(self,rhs):
        return type(self) == type(rhs) and self.name == rhs.name



class Object:

    def __init__(self,type,value = None):
        self.type = type
        if hasattr(self.type,"init"):
            self.type.init(self,value)
        else:
            self.value = value

    def op(self,op,arg = None):
        #print self
        if hasattr(self.type,"op_"+op):
            func = getattr(self.type,"op_"+op)
            if arg is not None:
                return func(self,arg)
            else:
                return func(self)
        else:
            #print "lhs :", self
            #print "rhs: ", arg
            raise UnsupportedOPError(op)

    def alloc(self,size = 1):
        self.type.alloc(self,size)

    def __nonzero__(self):
        return bool(self.value)

    def __repr__(self):
        return "SmallC Object <" + repr(self.type) + " : " + repr(self.value) +  ">"

    __str__ = __repr__

class ConstObject(Object):

    def op(self,op,arg = None):
        if op == "assign" or op == "inc" or op == "inc_" or op == "dec" or op == "dec_":
            pass # raise Error
        else:
            return Object.op(self,op,arg)
            #return super(ConstObject, self).op(op,arg)

    def __repr__(self):
        return "SmallC Const Object <" + repr(self.value) + " : " +  self.type.name+  ">"


#some special values

undefined = Object(Type)
void = Void()
nullType = Array(void)
null = Object(nullType)

