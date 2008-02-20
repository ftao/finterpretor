#coding=gbk
'''
Small C ����ֻ���������͡�
1. ����
2. Void
3. ����
4. �ṹ�� �����飩
ע��������������������java �����û��ơ�
�������������null ֵ�� ����Object(nullType,"Null Value") ����ʾ��
�ӳ����п��Կ��� null �ƺ����Ը�ֵ���κ����͵Ķ���(������������)


�Ӹ���ʾ�������������ƺ�  ����Ĭ��ֵΪ0 ,����Ĭ��ֵΪnull
һ���ṹ�壬member Ҳ����������ʼ����
�����ڵ�ʵ��û����ô�졣�� ������
'''
import operator
import sys
import interpretor.smallc.error as error


#���η�����
def require_same(func):
    def wrapped(self,lhs,rhs):
        if (rhs.type != self):
            raise error.TypeError(self,rhs)
        return func(self,lhs,rhs)
    return wrapped

def require_same_or_null(func):

    def wrapped(self,lhs,rhs):
        if (rhs.type != self and rhs.type != nullType):
            raise error.TypeError(self,rhs)
        return func(self,lhs,rhs)
    return wrapped

def require_not_empty(func):
    def wrapped(self,lhs,rhs):
        if lhs.value is None:
            raise error.EmptyReferenceError(lhs)
        return func(self,lhs,rhs)
    return wrapped


class Type:
    '''SmallC �������ͻ���
    ֧�ֵĵĲ����� assign , eq , ne, tcast
    '''
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
        'ǿ������ת��'
        if obj.type == type:
            return obj
        elif type == void:
            return Object(type)
        else:
            raise error.TCastError(obj,type)


    def alloc(self,size = None):
        'ͳһ�Ŀռ������ԣ�����ķ���ʵ����������� alloc_one ����'
        if size:
            ret = Object(Array(self))
            ret.value = [self.alloc() for i in range(size.value)]
            return ret
        else:
            return self.alloc_one()


    def __eq__(self,rhs):
        return self.name == rhs.name

    def __ne__(self,rhs):
        return not self.__eq__(rhs)

    def __repr__(self):
        return "<SmallC Type %s>" %self.name

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
        print obj.value,


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

    #����Ϊ��Ŀ����

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
        'int �Ŀռ���䷽���� ���ó�ֵΪ0.'
        #TODO is default value 0 OK ?
        return Object(self,0)


class Array(Type):
    '''Array
    ����һά�ģ���ά������������������
    '''
    def __init__(self,base,dim = 1):
        if dim > 1:
            self.base = Array(base, dim-1)
        else:
            self.base = base
        self.name = self.base.name + "[]"

    def op_print(self,obj):
        print obj.value,

    @require_same_or_null
    def op_assign(self,lhs,rhs):
        lhs.value = rhs.value
        return lhs

    @require_same_or_null
    @require_not_empty
    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value is rhs.value))

    @require_same_or_null
    @require_not_empty
    def op_ne(self,lhs,rhs):
        return Object(intType, int(not (lhs.value is rhs.value)))

    @require_not_empty
    def op_index(self,lhs,rhs):
        if rhs.type != intType:
            raise error.TypeError(intType,rhs)
        if lhs.value == null.value:
            raise error.NullError(lhs)

        ind = rhs.value
        if ind < 0 or ind >= len(lhs.value):
            raise error.IndexError(lhs.value,(0,len(lhs.value)))
        return lhs.value[ind]

#    def op_member(self,lhs,rhs):
#        '''
#        array ֻ֧��һ��member length
#        '''
#        if rhs != "length":
#            raise error.MemberError(lhs,rhs)
#        else:
#            return Object(intType,len(lhs.value))

    def alloc_one(self):
        return Object(self)



class Struct(Type):

    def __init__(self,name):
        self.name = name
        self.members = {}

    def op_print(self,lhs):
        print lhs

    def add_member(self,type,member_name):
        self.members[member_name] = type

    @require_same_or_null
    def op_assign(self,lhs,rhs):
        lhs.value = rhs.value
        return lhs


    @require_same_or_null
    @require_not_empty
    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value is rhs.value))

    @require_same_or_null
    @require_not_empty
    def op_ne(self,lhs,rhs):
        return Object(intType, int(not (lhs.value is rhs.value)))


    @require_not_empty
    def op_member(self,lhs,rhs):
        if not isinstance(rhs,str):
            raise error.TypeError("id",rhs)
        if lhs.value == null.value:
            raise error.NullError(lhs)
        if rhs not in self.members:
            raise error.MemberError(lhs,rhs)

        return lhs.value[rhs]


    def __repr__(self):
        ret = "<SmallC Type %s{" %self.name
        ret += ",".join(["%s:%s" %(x,self.members[x].name) for x in self.members])
        ret += "}>"
        return ret

    def alloc_one(self):
        ret = Object(self)
        ret.value = {}
        for name in self.members:
            ret.value[name] = Object(self.members[name])
        return ret


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

    def __not__(self):
        return not self.__nonzero__()

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
            raise error.UnsupportedOPError(op)
        else:
            return Object.op(self,op,arg)

    def __repr__(self):
        return "SmallC Const Object <" + repr(self.value) + " : " +  self.type.name+  ">"

    __str__ = __repr__

#some special values

intType = Integer()
void = Void()
nullType = NullType()
null = ConstObject(nullType,"NULL VALUE")

