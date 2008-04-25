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
        '''根据操作名和参数检查是否满足类型约束'''
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



