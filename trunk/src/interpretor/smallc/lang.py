#coding=gbk
'''
Small C ����ֻ���������͡�
1. ����
2. Void
3. ����
4. �ṹ�� �����飩
ע��������������������java �����û��ơ�
null ��ʾ�����á�
�������������null ֵ�� ����Object(nullType,None) ����ʾ��
�ӳ����п��Կ��� null �ƺ����Ը�ֵ���κ����͵Ķ���


'''
import operator
import sys
import interpretor.smallc.error as error

#class Singleton(type):
#    def __call__(cls, *args):
#        if not hasattr(cls, 'instance'):
#            cls.instance = super(Singleton, cls).__call__(*args)
#        return cls.instance

#���η�����

def require_same(func):
    def wrapped(self,lhs,rhs):
        if (rhs.type != self):
            raise error.TypeError(rhs,self)
        return func(self,lhs,rhs)
    return wrapped

def require_same_or_null(func):
    def wrapped(self,lhs,rhs):
        if (rhs.type != self and rhs.type != nullType):
            raise error.TypeError(self,rhs.type)
        return func(self,lhs,rhs)
    return wrapped

def require_int(func):
    def wrapped(self,lhs,rhs):
        if (rhs.type != intType):
            raise error.TypeError(self,rhs.type)
        return func(self,lhs,rhs)
    return wrapped

def require_str(func):
    def wrapped(self,lhs,rhs):
        if (not isinstance(rhs,str)):
            raise error.TypeError("id",rhs.type)
        return func(self,lhs,rhs)
    return wrapped



class Type:
    def __init__(self):
        self.name = "type"

    @require_same
    def op_assign(self,lhs,rhs):
        lhs.value = rhs.value
        return lhs

    @require_same
    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value is rhs.value))

    @require_same
    def op_ne(self,lhs,rhs):
        ret = self.op_eq(lhs,rhs)
        ret.value = [1,0][ret.value]
        return ret


    def op_tcast(self,obj,type):

        if obj.type == type:
            ret = obj
        else:
            ret = Object(type) # TODO raise error ?
        return ret

    def alloc(self,size = None):
        if size:
            ret = Object(Array(self))
            ret.value = [self.alloc() for i in range(size.value)]
            return ret
        else:
            return self.alloc_one()

    def __repr__(self):
        return "<SmallC Type %s>" %self.name

    def __eq__(self,rhs):
        return type(self) == type(rhs)

    def __ne__(self,rhs):
        return not self.__eq__(rhs)

    __str__ = __repr__


class Void(Type):
    def __init__(self):
        self.name = "void"


class Integer(Type):
    '''Small C ��������'''

    def __init__(self):
        self.name = "int"

    def asBool(self,obj):
        return bool(obj.value)

    def op_print(self,obj):
        #print "op_print",obj
        #sys.stderr.write(str(obj.value) + " ")
        print >>sys.stderr, obj.value


    @require_same
    def op_or(self,lhs,rhs):
        return Object(intType, int(bool(lhs.value or rhs.value)))

    @require_same
    def op_and(self,lhs,rhs):
        return Object(intType, int(bool(lhs.value and rhs.value)))

    @require_same
    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value == rhs.value))

    @require_same
    def op_ne(self,lhs,rhs):
        return Object(intType, int(lhs.value != rhs.value))

    @require_same
    def op_lt(self,lhs,rhs):
        return Object(intType, int(lhs.value < rhs.value))

    @require_same
    def op_gt(self,lhs,rhs):
        return Object(intType, int(lhs.value > rhs.value))

    @require_same
    def op_le(self,lhs,rhs):
        return Object(intType, int(lhs.value <= rhs.value))

    @require_same
    def op_ge(self,lhs,rhs):
        return Object(intType, int(lhs.value >= rhs.value))
    @require_same
    def op_add(self,lhs,rhs):
        return Object(intType, lhs.value + rhs.value)

    @require_same
    def op_minus(self,lhs,rhs):
        return Object(intType, lhs.value - rhs.value)

    @require_same
    def op_mul(self,lhs,rhs):
        return Object(intType, lhs.value * rhs.value)

    @require_same
    def op_div(self,lhs,rhs):
        return Object(intType, lhs.value / rhs.value)

    @require_same
    def op_mod(self,lhs,rhs):
        return Object(intType, lhs.value % rhs.value)


    def op_minus_(self,rhs):
        return Object(intType, - rhs.value)

    def op_not(self,rhs):
        return Object(intType, int(not rhs.value) )

    def op_inc(self,rhs):
        rhs.value += 1
        return rhs

    def op_dec(self,rhs):
        rhs.value -= 1
        return rhs

    def op_chk(self,rhs):
        if rhs.value == 0:
            raise error.ChkFailError()
        return rhs

    def op_inc_(self,lhs):
        ret = Object(intType, lhs.value)
        lhs.value += 1
        return ret

    def op_dec_(self,lhs):
        ret = Object(intType, lhs.value)
        lhs.value -= 1
        return ret

    def alloc_one(self):
        return Object(self,0)


class Array(Type):
    '''Array ������C�е�ָ�롣
    ��ֵ�����������
    1.δ��ʼ�� []
    2.null 0
    3.���� һ���ǿ��б�
    '''

    def __init__(self,base,dim = 1):
        if dim > 1:
            self.base = Array(base, dim-1)
        else:
            self.base = base
        self.dim = 1
        self.name = self.base.name + "[]" * self.dim

    def __eq__(self,rhs):
        return type(self) == type(rhs) and self.base == rhs.base


    def op_print(self,obj):
        print obj.value,

    @require_same_or_null
    def op_assign(self,lhs,rhs):
        lhs.value = rhs.value
        return lhs

    @require_same_or_null
    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value is rhs.value))

    @require_same_or_null
    def op_ne(self,lhs,rhs):
        return Object(intType, int(not (lhs.value is rhs.value)))

    def op_index(self,lhs,rhs):
        if rhs.type != intType or lhs.value is None:
            raise Error.TypeError(lhs,rhs)
        ind = rhs.value
        if ind < 0 or ind >= len(lhs.value):
            raise error.IndexError(lhs.value,(0,len(lhs.value)))
        return lhs.value[ind]


    def alloc_one(self):
        return Object(self)



class Struct(Type):

    def __init__(self,name):
        self.name = name
        self.members = {}

    def add_member(self,type,member_name):
        self.members[member_name] = type

    @require_same_or_null
    def op_assign(self,lhs,rhs):
        lhs.value = rhs.value
        return lhs


    @require_same_or_null
    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value is rhs.value))

    @require_same_or_null
    def op_ne(self,lhs,rhs):
        return Object(intType, int(not (lhs.value is rhs.value)))


    def op_member(self,lhs,rhs):
        if lhs.value is None:
            raise error.NullError(lhs)
        if not isinstance(rhs,str):
            raise error.TypeError("id",lhs)
        if rhs not in self.members:
            raise error.MemberError(lhs,rhs)

        return lhs.value[rhs]


    def __repr__(self):
        ret = "<SmallC Type %s{" %self.name
        ret += ",".join(["%s:%s" %(x,self.members[x].name) for x in self.members])
        ret += "}>"
        return ret

    def __eq__(self,rhs):
        return type(self) == type(rhs) and self.name == rhs.name

    def alloc_one(self):
        ret = Object(self)
        ret.value = {}
        for name in self.members:
            ret.value[name] = Object(self.members[name])
        return ret

    def alloc(self,size = None):
        if size:
            ret = Object(Array(self))
            ret.value = [self.alloc() for i in range(size.value)]
            return ret
        else:
            return self.alloc_one()

class NullType(Type):
    def asBool(self,obj):
        return False

    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.type == rhs.type and lhs.value is rhs.value))

    def op_ne(self,lhs,rhs):
        return Object(intType, int(lhs.type != rhs.type or lhs.value is not rhs.value))


class Object:

    def __init__(self,type,value = None):
        self.type = type
        self.value = value
        #TODO ugly here
        if value is None and type is intType:
            self.value = 0


    def __nonzero__(self):
        if hasattr(self.type, "asBool"):
            return self.type.asBool(self)
        else:
            #raise Erro (cant't convert to bool value)
            return bool(self.value)

    def op(self,op,arg = None):
        if hasattr(self.type,"op_"+op):
            func = getattr(self.type,"op_"+op)
            if arg is not None:
                return func(self,arg)
            else:
                return func(self)
        else:
            raise error.UnsupportedOPError(op)


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

intType = Integer()
void = Void()
nullType = NullType()
null = Object(nullType,None)

