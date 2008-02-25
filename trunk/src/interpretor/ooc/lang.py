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
import interpretor.ooc.error as error
import interpretor

#class Singleton(type):
#    def __call__(cls, *args):
#        if not hasattr(cls, 'instance'):
#            cls.instance = super(Singleton, cls).__call__(*args)
#        return cls.instance


#���η�����
def require_same(func):
    def wrapped(self,lhs,rhs):
        if (rhs.type != self):
            raise error.TypeError(self,rhs.type)
        return func(self,lhs,rhs)
    return wrapped

def require_same_or_null(func):

    def wrapped(self,lhs,rhs):
        if (rhs.type != self and rhs.type != nullType):
            raise error.TypeError(self,rhs.type)
        return func(self,lhs,rhs)
    return wrapped

def require_same_base_or_null(func):
    '''
    �Ƿ����ݣ� ������ԭ�������͡���������ԭ��������
    ������   Object -> CA -> CB -> CC

    '''
    def wrapped(self,lhs,rhs):
        base = rhs.org_type
        if base == nullType:
            return func(self,lhs,rhs)
        while(base):
            if base == lhs.org_type:
                break
            else:
                base = base.base
        else:#break out so mathces
            raise error.TypeError(lhs.org_type,rhs.org_type)
        return func(self,lhs,rhs)
    return wrapped

def is_type_castable(obj,type):
    '''����Ƿ���Խ�obj ת���� type ����'''
    base = obj.type
    while(base):
        if base == type:
            break
        else:
            base = base.base
    else:
        return False
    return True

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
        '''����ǿ��ת����
        1.��ͬ�������ǿ���ת��
        2.���������ת��
        3.�κ�������void ת��
        ת�����ֵ������������
        obj.org_type  = type
        obj.type ����
        '''
        if obj.type == type:
            return obj
        elif type == void:
            return Object(void)
        else:
            if is_type_castable(obj,type):
                obj.org_type = type
                return obj
            else:
                raise error.TCastError(obj,type)

    def alloc(self,size = None):
        if size:
            ret = Object(Array(self))
            ret.value = [self.alloc() for i in range(size.value)]
            return ret
        else:
            return self.alloc_one()

    def __repr__(self):
        return "<ooc Type %s>" %self.name

    def __eq__(self,rhs):
        return self.name == rhs.name

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
    '''Array
    '''

    def __init__(self,base,dim = 1):
        if dim > 1:
            self.base = Array(base, dim-1)
        else:
            self.base = base
        self.name = self.base.name + "[]"

    def op_print(self,obj):
        print '[',
        for x in self.value:
            x.op("print")
        print ']',

    @require_same
    def op_assign(self,lhs,rhs):
        lhs.value = rhs.value
        return lhs

    @require_same
    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value is rhs.value))

    @require_same
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

    def op_member_no_private(self,lhs,rhs):
        '''
        array ֻ֧��һ��member length
        '''
        if rhs != "length":
            raise error.MemberError(lhs,rhs)
        else:
            return Object(intType,len(lhs.value))

class RootClass(Type):
    '''���������һ����Java �ĵ��������ԡ� �������������Ļ���'''
    def __init__(self):
        self.name = "Object"
        self.base = None

    @require_same_base_or_null
    def op_assign(self,lhs,rhs):
        lhs.type = rhs.type
        lhs.value = rhs.value
        return lhs

    @require_same_base_or_null
    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value is rhs.value))

    @require_same_base_or_null
    def op_ne(self,lhs,rhs):
        return Object(intType, int(not (lhs.value is rhs.value)))


    def insert_public(self,value):
        pass

    def get_cls_member(self, name, no_private = False):
        '''��һ����Ψһ�ĳ�Ա�� ����static , const ���� �����з���
        '''
        raise error.MemberError(self,name)


    def op_member(self,lhs,rhs):
        '''
        ins.var �������͵�����.
        ���Ի�õ�ǰ���˽�У����кͻ���Ĺ��г�Ա
        '''
        #print "get %s from  %s" %(rhs,lhs)
        if not isinstance(rhs,str):
            raise error.TypeError("id",lhs)
        raise error.MemberError(lhs,rsh)

    def op_member_no_private(self,lhs,rhs):
        '''
        ins.var �������͵�����
        ���ַ���ֻ���Ի�����������public ��Ա
        '''
        if not isinstance(rhs,str):
            raise error.TypeError("id",lhs)
        raise error.MemberError(lhs,rsh)

    def op_member_cls(self,name):
        raise error.MemberError(self, name)

class Class(RootClass):
    '''OOC ���Ե��ࡣ
    ����redef ��Ա��Ϊ��public
    ����public,const ��Ϊ��public
    ֻ��private ����private
    '''
    def __init__(self,name,global_ns,base = None,decorate = None):
        self.name = name
        if base is None:
            self.base = rootClass
        else:
            self.base = base
        self.global_ns = global_ns
        self.decorate = decorate
        self.members = {}
        self.by_decorate = {
            'static':[],
            'private':[],
            'public':[],
            'static':[],
            'redef':[],
            'const':[]
        }
        self.by_type = {
            'var':[],
            'func':[]
        }
        self.cls_var = {}


    def add_var(self,name,value,decorate):
        self.members[name] = (value,decorate)
        self.by_type['var'].append(name)
        self.by_decorate[decorate].append(name)
        if decorate  == "static":
            self.cls_var[name] = Object(value)
        elif decorate == "const":
            self.cls_var[name] = value

    def add_func(self,name,value,decorate):
        self.members[name] = (value,decorate)
        self.by_type['func'].append(name)
        self.by_decorate[decorate].append(name)



    def op_print(self, obj):
        print "<%s Instanse at %s>" %(obj.type.name, id(obj.value))


    def op_get(self,lhs,rhs):
        #print "get %s from %s" %(rhs,lhs)
        try:
            return self.op_member(lhs,rhs)
        except error.MemberError:
            return self.global_ns.get(rhs)

    def op_member(self,lhs,rhs):
        '''
        ins.var �������͵�����.
        ���Ի�õ�ǰ���˽�У����кͻ���Ĺ��г�Ա
        '''
        #print "get %s from  %s" %(rhs,lhs)
        if not isinstance(rhs,str):
            raise error.TypeError("id",lhs)

        if rhs in lhs.value:
            #ʵ������ �Լ��Ļ�����
            return lhs.value[rhs]
        else:
            #�����/����
            ret = self.get_cls_member(rhs)
            if rhs in self.by_type['func']:
                ret = (ret,lhs)
            return ret

    def op_member_no_private(self,lhs,rhs):
        '''
        ins.var �������͵�����
        ���ַ���ֻ���Ի�����������public ��Ա
        '''
        if not isinstance(rhs,str):
            raise error.TypeError("id",lhs)
        if rhs in self.by_decorate['private']:
            raise error.MemberError(lhs, rhs)

        if rhs in lhs.value:
            #ʵ������ �Լ��Ļ�����
            return lhs.value[rhs]
        else:
            #�����/����
            ret = self.get_cls_member(rhs, True)
            if rhs in self.by_type['func']:
                ret = (ret,lhs)
            return ret


    def insert_public(self,value):
        if self.base:
            self.base.insert_public(value)
        for name in self.by_type['var']:
            if self.members[name][1] in ("public", "redef"):
                value[name] = Object(self.members[name][0])
        return value

    def get_cls_member(self, name, no_private = False):
        '''��һ����Ψһ�ĳ�Ա�� ����static , const ���� �����з���
        '''
        if no_private and name in self.by_decorate['private']:
            #TODO Ӧ����һ�����õ���ʾ
            raise error.MemberError(self,name)

        if name in self.cls_var: #�������static �� const ����
            return self.cls_var[name]
        elif name in self.by_type["func"]: #����
            return self.members[name][0]
        else:
            return self.base.get_cls_member(name,True) #�����˽�г�Ա���ǲ��ܷ��ʵ�

    def op_get_cls(self,name):
        '''��static �����п��Է��ʵ����ֿռ�
        '''
        try:
            return self.op_member_cls(name)
        except error.MemberError:
            return self.global_ns.get(name)

    def op_member_cls(self,name):
        '''
         �� ClassA.var  �����ĵ��ó���ʱִ�еĲ���
        TODO: �Ƿ��Ǽ̳У�
        '''
        if name in self.cls_var: #static ��const ����
            return self.cls_var[name]
        elif name in self.by_type['func'] and name in self.by_decorate["static"]: #static ����
            return (self.members[name][0],None)
        else: #���û���
            return self.base.op_member_cls(name)


    def alloc_one(self):
        ret = Object(self)
        ret.value = {}
        self.base.insert_public(ret.value)
        for name in self.by_type['var']:
            if self.members[name][1] not in ['const','static']:
                ret.value[name] = Object(self.members[name][0])
        return ret

    def __repr__(self):
        ret = "<OOC Type %s{" %self.name
        ret += "}>"
        return ret


class NullType(Type):

    def __init__(self):
        self.name = "NullType"
        self.base = None

    def asBool(self,obj):
        return False

    @require_same_base_or_null
    def op_assign(self,lhs,rhs):
        lhs.type = rhs.type
        lhs.value = rhs.value
        return lhs

    def op_eq(self,lhs,rhs):
        if isinstance(rhs.type,(RootClass,NullType)):
            return Object(intType, int(lhs.value is rhs.value))
        else:
            raise error.TypeError(lhs,rhs)

    def op_ne(self,lhs,rhs):
        if isinstance(rhs.type,(RootClass,NullType)):
            return Object(intType, int(lhs.value is not  rhs.value))
        else:
            raise error.TypeError(lhs,rhs)

    def op_tcast(self,obj,type):
        '''����ǿ��ת��
        NullType ����ת�����κ�����RootClass �� Class ����
        '''
        if isinstance(type,(RootClass,NullType)):
            obj.ort_type = type
            return obj
        else:
            raise error.TCastError(obj,type)

    def __repr__(self):
        return "<ooc Type Null>"

    __str__ = __repr__

class Object:

    def __init__(self,type,value = None):
        self.type = type
        self.org_type = type
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
        return "OOC Object <" + repr(self.type) + " : " + repr(self.value) +  ">"

    __str__ = __repr__

class ConstObject(Object):

    def op(self,op,arg = None):
        if op == "assign" or op == "inc" or op == "inc_" or op == "dec" or op == "dec_":
            raise error.UnsupportedOPError(op)
        else:
            return Object.op(self,op,arg)

    def __repr__(self):
        return "OOC Const Object <" + repr(self.value) + " : " +  self.type.name+  ">"

    __str__ = __repr__

#some special values

intType = Integer()
void = Void()
rootClass = RootClass()
nullType = NullType()
null = ConstObject(nullType,None)

