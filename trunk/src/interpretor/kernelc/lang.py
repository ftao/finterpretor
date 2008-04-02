#coding=utf8
'''
KernelC 只有一个 int 类型。
同时数字有可以作为变量名。 使用* 操作符。
'''
import interpretor.kernelc.error as error
class Type:

    def op_print(self, obj):
        print obj.value,

    def op_println(self, obj):
        print obj.value

class Void(Type):
    def __init__(self):
        self.name = "void"

class Integer(Type):
    '''Kernel C 整数类型'''

    def __init__(self):
        self.name = "int"

    def asBool(self,obj):
        return bool(obj.value)

    def op_assign(self, lhs, rhs):
        lhs.value = rhs.value
        return lhs

    def op_chk(self, obj):
        if obj.value == 0:
            raise error.ChkFailError()
        else:
            return obj

    def op_or(self,lhs,rhs):
        return Object(intType, int(bool(lhs.value or rhs.value)))


    def op_and(self,lhs,rhs):
        return Object(intType, int(bool(lhs.value and rhs.value)))


    def op_eq(self,lhs,rhs):
        return Object(intType, int(lhs.value == rhs.value))


    def op_ne(self,lhs,rhs):
        return Object(intType, int(lhs.value != rhs.value))


    def op_lt(self,lhs,rhs):
        return Object(intType, int(lhs.value < rhs.value))


    def op_gt(self,lhs,rhs):
        return Object(intType, int(lhs.value > rhs.value))


    def op_le(self,lhs,rhs):
        return Object(intType, int(lhs.value <= rhs.value))


    def op_ge(self,lhs,rhs):
        return Object(intType, int(lhs.value >= rhs.value))


    def op_add(self,lhs,rhs):
        return Object(intType, lhs.value + rhs.value)


    def op_minus(self,lhs,rhs):
        return Object(intType, lhs.value - rhs.value)


    def op_mul(self,lhs,rhs):
        return Object(intType, lhs.value * rhs.value)


    def op_div(self,lhs,rhs):
        return Object(intType, lhs.value / rhs.value)


    def op_mod(self,lhs,rhs):
        return Object(intType, lhs.value % rhs.value)

    #以下为单目操作

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

    def op_inc_(self,lhs):
        ret = Object(intType, lhs.value)
        lhs.value += 1
        return ret

    def op_dec_(self,lhs):
        ret = Object(intType, lhs.value)
        lhs.value -= 1
        return ret


class Object:

    def __init__(self, type, value = None, is_left_value = False):
        self.type = type
        self.value = value

        self.is_left_value = is_left_value
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
            if (not self.is_left_value) and op == "assign":
                raise error.NotLeftValueError()
            func = getattr(self.type,"op_"+op)
            if arg is not None:
                return func(self,arg)
            else:
                return func(self)
        else:
            #pass
            raise error.UnsupportedOPError(op)

    def __repr__(self):
        return str((self.type ,self.value))

    __str__ = __repr__

intType = Integer()
void = Void()