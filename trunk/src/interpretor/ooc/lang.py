#coding=utf8
'''
Small C 语言只有三种类型。
1. 整形
2. Void
3. 数组
4. 结构体 （数组）
注意这个里面变量名是类似java 的引用机制。
null 表示空引用。
怎样处理特殊的null 值？ （用Object(nullType,None) 来表示。
从程序中可以看到 null 似乎可以赋值给任何类型的对象。


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


#修饰符函数
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
    是否相容？

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
    '''检测是否可以将obj 转换成 type 类型'''
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

    def to_str(self,obj):
        return  str(obj.value)

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
        '''类型强制转换。
        1.相同类型总是可以转换
        2.子类向基类转换
        3.任何类型向void 转换
        转换后的值有如下特征：
        obj.org_type  = type
        obj.type 不变
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
    '''Small C 整数类型'''

    def __init__(self):
        self.name = "int"

    def asBool(self,obj):
        return bool(obj.value)

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

    def to_str(self,obj):
        return '[' + ",".join([x.to_str() for x in self.value]) + ']'

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
            raise error.TypeError(lhs,rhs)
        ind = rhs.value
        if ind < 0 or ind >= len(lhs.value):
            raise error.IndexError(lhs.value,(0,len(lhs.value)))
        return lhs.value[ind]


    def alloc_one(self):
        return Object(self)

    def op_member_no_private(self,lhs,rhs):
        '''
        array 只支持一个member length
        '''
        if rhs != "length":
            raise error.MemberError(lhs,rhs)
        else:
            return Object(intType,len(lhs.value))

class RootClass(Type):
    '''这个语言是一个类Java 的单根的语言。 这个类是所有类的基类'''
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
        '''对一个类唯一的成员。 包括static , const 变量 和所有方法
        '''
        raise error.MemberError(self,name)


    def op_member(self,lhs,rhs):
        '''
        ins.var 这种类型的引用.
        可以获得当前类的私有，公有和基类的公有成员
        '''
        #print "get %s from  %s" %(rhs,lhs)
        if not isinstance(rhs,str):
            raise error.TypeError("id",lhs)
        raise error.MemberError(lhs,rhs)

    def op_member_no_private(self,lhs,rhs):
        '''
        ins.var 这种类型的引用
        这种方法只可以获得类或其基类的public 成员
        '''
        if not isinstance(rhs,str):
            raise error.TypeError("id",lhs)
        raise error.MemberError(lhs,rhs)

    def op_member_cls(self,name):
        raise error.MemberError(self, name)

class Class(RootClass):
    '''OOC 语言的类。
    所有redef 成员认为是public
    所有public,const 认为是public
    只有private 才是private
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


    def op_get(self,lhs,rhs):
        #print "get %s from %s" %(rhs,lhs)
        try:
            return self.op_member(lhs,rhs)
        except error.MemberError:
            return self.global_ns.get(rhs)

    def op_member(self,lhs,rhs):
        '''
        ins.var 这种类型的引用.
        可以获得当前类的私有，公有和基类的公有成员
        '''
        #print "get %s from  %s" %(rhs,lhs)
        if not isinstance(rhs,str):
            raise error.TypeError("id",lhs)

        if rhs in lhs.value:
            #实例变量 自己的或基类的
            return lhs.value[rhs]
        else:
            #类变量/函数
            ret = self.get_cls_member(rhs)
            if rhs in self.by_type['func']:
                ret = (ret,lhs)
            return ret

    def op_member_no_private(self,lhs,rhs):
        '''
        ins.var 这种类型的引用
        这种方法只可以获得类或其基类的public 成员
        '''
        if not isinstance(rhs,str):
            raise error.TypeError("id",lhs)
        if rhs in self.by_decorate['private']:
            raise error.MemberError(lhs, rhs)

        if rhs in lhs.value:
            #实例变量 自己的或基类的
            return lhs.value[rhs]
        else:
            #类变量/函数
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
        '''对一个类唯一的成员。 包括static , const 变量 和所有方法
        '''
        if no_private and name in self.by_decorate['private']:
            #TODO 应该用一个更好的提示
            raise error.MemberError(self,name)

        if name in self.cls_var: #类变量，static 和 const 变量
            return self.cls_var[name]
        elif name in self.by_type["func"]: #方法
            return self.members[name][0]
        else:
            return self.base.get_cls_member(name,True) #基类的私有成员总是不能访问的

    def op_get_cls(self,name):
        '''在static 方法中可以访问的名字空间
        '''
        try:
            return self.op_member_cls(name)
        except error.MemberError:
            return self.global_ns.get(name)

    def op_member_cls(self,name):
        '''
         当 ClassA.var  这样的调用出现时执行的操作
        TODO: 是否考虑继承？
        '''
        if name in self.cls_var: #static 和const 变量
            return self.cls_var[name]
        elif name in self.by_type['func'] and name in self.by_decorate["static"]: #static 函数
            return (self.members[name][0],None)
        else: #调用基类
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
        '''类型强制转换
        NullType 可以转换成任何类型RootClass 或 Class 类型
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

    def to_str(self):
        return self.type.to_str(self)

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
