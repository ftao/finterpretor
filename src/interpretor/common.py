#coding=utf8
#$Id$


class TypeConstraint:
    '''类型约束,用于静态类型检查
    具体规则不同语言可能不一样，但是一些公共的函数，结构可以公用.
    '''
    error_template = "Type Constraint Check failed on line %s , for %s. "

    def __init__(self):
        self._rules = {}

    def report_error(self, line, *operands):
        print self.error_template %(line, str(operands))

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

    def add(self, op_name, req):
        if op_name not in self._rules:
            self._rules[op_name] = []
        self._rules[op_name].append(req)

    def check(self, op_name, *operands):

        for func in self._rules[op_name]:
            if not func(*operands):
                print "check type failed on " , func, "for" , operands
                return False
        return True