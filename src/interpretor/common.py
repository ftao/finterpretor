#coding=utf8
#$Id$


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
    def is_a(type, which = None):
        '''是否是类型....
         注意type 是语言类型对应的Python 类。（比如Integer, Array, Struct 等等 而不是
        intType , Void 等等
        '''
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
    def is_in(type_set, which = None):
        ''' type_set 的含义见上面(is_a)的说明'''
        def wrapped(*operands):
            if which is None:
                for x in operands:
                    if not x.__class__ in type_set :
                        return False
                return True
            else:
                return operands[which].__class__ in type_set
        return wrapped


    @staticmethod
    def has_op(op_name, operand):
        return hasattr(operand, "op_" + op_name)


    def add(self, op_name, cons, for_type = 'all'):

        if op_name not in self._rules:
            self._rules[op_name] = []
        self._rules[op_name].append((for_type, cons))


    def check(self, op_name, *operands):
        '''根据操作名和参数检查是否满足类型约束'''
        assert len(operands) >= 1 #操作数总至少有一个吧？
        #print operands
        #首先我们需要类型是否支持该操作符
        if not self.has_op(op_name, operands[0]):
            print "operation %s is supported by the %s " %(op_name, operands[0])
            return False
        if op_name in self._rules:
            for (for_type, func) in self._rules[op_name]:
                if for_type != 'all' and not isinstance(operands[0], for_type):
                    continue
                if not func(*operands):
                    print "check type failed on " , func, "for" , op_name , " with " , operands
                    return False
        return True



