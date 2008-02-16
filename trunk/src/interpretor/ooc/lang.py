#coding=gbk
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
    是否相容？ 看的是原来的类型。自身看的是原来的类型
    '''
    def wrapped(self,lhs,rhs):
        base = rhs.real_type
        if base == nullType:
            return func(self,lhs,rhs)
        while(base):
            if base == self:
                break
            else:
                try:
                    base = base.base
                except AtrributeError,e:
                    base = None
        else:#break out so mathces
            raise error.TypeError(self,rhs.real_type)
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
            raise error.TCastError(obj,type)
        return ret

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

    def op_print(self,obj):
        print >>sys.stderr,obj.value,


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


class Class(Type):

    def __init__(self,name,global_ns,base = None,decorate = None):
        self.name = name
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

    def op_print(self,lhs):
        print "op_print..............",lhs

    @require_same_base_or_null
    def op_assign(self,lhs,rhs):
        if rhs.real_type != self: #实际类型改变了
            #print "%s type changes to %s" %(lhs,rhs.type)
            lhs.real_type = rhs.real_type
        lhs.value = rhs.value
        #print lhs
        return lhs


    @require_same_base_or_null
    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value is rhs.value))

    @require_same_base_or_null
    def op_ne(self,lhs,rhs):
        return Object(intType, int(not (lhs.value is rhs.value)))

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
        if lhs.value is None:
            raise error.NullError(lhs)
        if not isinstance(rhs,str):
            raise error.TypeError("id",lhs)

        if rhs in lhs.value:
            #实例变量 自己的或基类的
            return lhs.value[rhs]
        else:
            #类变量/函数
            #由于可能有子类来调用， 这里用real_type
            rt = lhs.real_type
            ret = rt.get_cls_member(rhs)
            if rhs in rt.by_type['func']:
                ret = (ret,lhs)
            return ret

    def op_member_no_private(self,lhs,rhs):
        '''
        ins.var 这种类型的引用
        这种方法只可以获得类或其基类的public 成员
        '''
        #print "get %s from  %s" %(rhs,lhs)
        if lhs.value is None:
            raise error.NullError(lhs)
        if not isinstance(rhs,str):
            raise error.TypeError("id",lhs)

        if rhs in lhs.value:
            #实例变量 自己的或基类的
            return lhs.value[rhs]
        else:
            #类变量/函数
            #由于可能有子类来调用， 这里用real_type
            rt = lhs.real_type
            ret = rt.get_cls_member(rhs)
            if rhs in rt.by_type['func']:
                ret = (ret,lhs)
            return ret
    def __repr__(self):
        ret = "<OOC Type %s{" %self.name
        #ret += ",".join(["%s:%s" %(x,self.members[x].name) for x in self.members])
        ret += "}>"
        return ret

    def alloc_one(self):
        ret = Object(self)
        ret.value = {}
        if self.base:
            self.base.insert_public(ret.value)
        for name in self.by_type['var']:
            if self.members[name][1] not in ['const','static']:
                ret.value[name] = Object(self.members[name][0])
        return ret

    def insert_public(self,value):
        if self.base:
            self.base.insert_public(value)
        for name in self.by_type['var']:
            if self.members[name][1] == "public":
                value[name] = Object(self.members[name][0])
        return value

    def get_cls_member(self, name, no_private = False):
        '''对一个类唯一的成员。 包括static , const 变量 和所有方法
        '''
        if no_private and name in self.by_decorate['private']:
            #TODO 应该用一个更好的提示
            raise error.MemberError(self,name)

        if name in self.cls_var:
            ret = self.cls_var[name]
            return ret
        elif name in self.by_type["func"]:
            return self.members[name][0]
        elif self.base:
            return self.base.get_cls_member(name,True) #基类的私有成员总是不能访问的
        else:
            raise error.MemberError(self,name)

    def op_get_cls(self,name):
        '''
        在static 方法中可以访问的名字空间
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
        if name not in self.members or self.members[name][1] not in ("static","const"):
            raise error.MemberError(self,name)
        if name in self.cls_var:
            return self.cls_var[name]
        if name in self.by_type['func'] and name in self.by_decorate["static"]:
            return (self.members[name][0],None)

    def op_tcast(self,obj,type):
        if obj.type == type:
            return obj
        elif type == void:
            return Object(void)
        else:
            ret = Object(type)
            try:
                ret.op("assign",obj)
            except error.TypeError:
                raise error.TCastError(obj,type)
            return ret

class NullType(Type):

    @require_same_base_or_null
    def op_assign(self,lhs,rhs):
        if rhs.type != self: #实际类型改变了
            #print "type changes to",rhs.type
            lhs.type = rhs.type
        lhs.value = rhs.value
        return lhs

    def asBool(self,obj):
        return False

    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.type == rhs.type and lhs.value is rhs.value))

    def op_ne(self,lhs,rhs):
        return Object(intType, int(lhs.type != rhs.type or lhs.value is not rhs.value))

    def __repr__(self):
        return "<ooc Type Null>"

    __str__ = __repr__

class Object:

    def __init__(self,type,value = None):
        self.type = type
        self.real_type = type
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
nullType = NullType()
null = ConstObject(nullType,None)

