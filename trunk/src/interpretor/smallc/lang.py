#coding=utf8
#$Id$

'''
Small C 语言只有三种类型。
1. 整形
2. Void
3. 数组
4. 结构体 （数组）
注意这个里面变量名是类似java 的引用机制。
怎样处理特殊的null 值？ （用Object(nullType,"Null Value") 来表示。
从程序中可以看到 null 似乎可以赋值给任何类型的对象。(除了整数对象)


从给的示例代码来看，似乎  整形默认值为0 ,其他默认值为null
一个结构体，member 也按这个规则初始化。
我现在的实现没有这么办。。 待讨论

关于类型约束:
1.赋值
2.操作符 （算术,逻辑)
3.函数参数传递
4.强制类型转换
'''
import interpretor.smallc.error as error

#类型约束
#这个应该作为语言定义的一部分
#所以放在这里是合适的
#但是类型计算规则呢？
#放在parse.py 里面作为语义动作?
#一条约束规则应该包含如下的内容
# * 操作符
# * 约束规则列表
#用一个简单的列表就可以
class TypeConstraint:
    '''类型约束,用于静态类型检查'''
    def __init__(self):
        self._rules = {}

    @staticmethod
    def is_same(*operands):
        if len(operands) != 2:
            return False
        else:
            return operands[0] == operands[1]

    @staticmethod
    def is_same_or_null(*operands):
        if(len(operands) != 2):
            return False #Something is wrong
        else:
            #TODO: should it be operands[1] = nullType ?
            return operands[0] == operands[1] or nullType in operands

    @staticmethod
    def is_castable(from_type, to_type):
        if from_type == to_type:
            return True
        elif to_type == void:
            return True
        else:
            return False


    @staticmethod
    def is_type(type, which = None):
        def wrapped(*operands):
            if which is None:
                for x in operands:
                    if not isinstance(x, type) :
                        return False
                return True
            else:
                return isinstance(operands[which], type)
        return wrapped

    @staticmethod
    def has_member(struct, member):
        return member in struct.members

    @staticmethod
    def has_op(op_name, operand):
        return hasattr(operand, "op_" + op_name)

    def add(self, op_name, req):
        if op_name not in self._rules:
            self._rules[op_name] = []
        self._rules[op_name].append(req)

    def check(self, op_name, *operands):
        assert len(operands) >= 1 #操作数总至少有一个吧？
        #print operands
        #首先我们需要类型是否支持该操作符
        if not self.has_op(op_name, operands[0]):
            print "operation %s is supported by the %s " %(op_name, operands[0])
            return False
        if op_name in self._rules:
            for func in self._rules[op_name]:
                if not func(*operands):
                    print "check type failed on " , func, "for" , op_name , " with " , operands
                    return False
        return True

#在静态类型检查时将要用到这个
type_constraint = TypeConstraint()


#修饰符函数,用于动态类型检查
def require_same(func):
    type_constraint.add(func.__name__.split('_')[1], TypeConstraint.is_same)
    def wrapped(self,lhs,rhs):
        if not TypeConstraint.is_same(self, rhs.type):
            raise error.TypeError(self,rhs)
        return func(self,lhs,rhs)
    return wrapped

def require_same_or_null(func):
    type_constraint.add(func.__name__.split('_')[1], TypeConstraint.is_same_or_null)
    def wrapped(self,lhs,rhs):
        if not TypeConstraint.is_same_or_null(self, rhs.type):
            raise error.TypeError(self,rhs)
        return func(self,lhs,rhs)
    return wrapped

def require_castable(func):
    type_constraint.add(func.__name__.split('_')[1], TypeConstraint.is_castable)
    def wrapped(self,lhs,rhs):
        if not TypeConstraint.is_castable(self, rhs):
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
    '''SmallC 语言类型基类
    支持的的操作有 assign , eq , ne, tcast
    '''
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

    @require_castable
    def op_tcast(self,obj,type):
        '强制类型转换'
        return Object(type, obj.value)


    def alloc(self, size = None):
        '统一的空间分配策略，具体的分配实现由子类完成 alloc_one 方法'
        if size:
            ret = Object(Array(self))
            ret.value = [self.alloc() for i in range(size.value)]
            return ret
        else:
            return self.alloc_one()

    def repr(self,obj):
        return repr(obj.value)

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

    #以下为单目操作

    def op_minus_(self, rhs):
        return Object(intType, - rhs.value)

    def op_not(self, rhs):
        return Object(intType, int(not rhs.value) )

    def op_inc(self, rhs):
        rhs.value += 1
        return rhs

    def op_dec(self, rhs):
        rhs.value -= 1
        return rhs

    def op_chk(self, rhs):
        if rhs.value == 0:
            raise error.ChkFailError()
        return rhs

    def op_inc_(self, lhs):
        ret = Object(intType, lhs.value)
        lhs.value += 1
        return ret

    def op_dec_(self, lhs):
        ret = Object(intType, lhs.value)
        lhs.value -= 1
        return ret

    def alloc_one(self):
        'int 的空间分配方法。 设置初值为0.'
        #TODO is default value 0 OK ?
        return Object(self,0)


class Array(Type):
    '''Array
    总是一维的，多维可以由数组的数组组成
    '''
    def __init__(self,base,dim = 1):
        if dim > 1:
            self.base = Array(base, dim-1)
        else:
            self.base = base
        self.name = self.base.name + "[]"

    def to_str(self,obj):
        return '[' + ",".join([x.to_str() for x in obj.value]) + ']'

    @require_same_or_null
    def op_assign(self,lhs,rhs):
        lhs.value = rhs.value
        return lhs

    @require_not_empty
    @require_same_or_null
    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value is rhs.value))

    @require_not_empty
    @require_same_or_null
    def op_ne(self,lhs,rhs):
        return Object(intType, int(not (lhs.value is rhs.value)))

    @require_not_empty
    def op_index(self, lhs, rhs):
        if rhs.type != intType:
            raise error.TypeError(intType,rhs)
        if lhs.value == null.value:
            raise error.NullError(lhs)

        ind = rhs.value
        if ind < 0 or ind >= len(lhs.value): #动态错误
            raise error.IndexError(rhs.value,(0,len(lhs.value)))
        return lhs.value[ind]

    def op_member(self,lhs,rhs):
        '''
        array 只支持一个member length
        '''
        if rhs != "length":
            raise error.MemberError(lhs,rhs)
        else:
            return Object(intType,len(lhs.value))

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


    @require_not_empty
    @require_same_or_null
    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value is rhs.value))

    @require_not_empty
    @require_same_or_null
    def op_ne(self,lhs,rhs):
        return Object(intType, int(not (lhs.value is rhs.value)))


    @require_not_empty
    def op_member(self,lhs,rhs):
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

    def to_str(self):
        return self.type.to_str(self)

    def __repr__(self):
        return self.type.repr(self)
        #return "SmallC Object <" + repr(self.type) + " : " + repr(self.value) +  ">"

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


type_constraint.add('argument_pass', TypeConstraint.is_same)
type_constraint.add('member', TypeConstraint.is_type(Struct))
type_constraint.add('member', TypeConstraint.has_member)
type_constraint.add('index', TypeConstraint.is_type(Array, 0))
type_constraint.add('index', TypeConstraint.is_type(Integer, 1))

#===============================================================================
# type_constraint.add('minus_', TypeConstraint.is_type(Integer, 0))
# type_constraint.add('not', TypeConstraint.is_type(Integer, 0))
# type_constraint.add('inc', TypeConstraint.is_type(Integer, 0))
# type_constraint.add('inc_', TypeConstraint.is_type(Integer, 0))
# type_constraint.add('dec', TypeConstraint.is_type(Integer, 0))
# type_constraint.add('dec_', TypeConstraint.is_type(Integer, 0))
#===============================================================================