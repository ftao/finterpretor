#coding=gbk
import copy
import interpretor.smallc.lang as lang
import interpretor.smallc.error as error

def copy_ns(ns_dict):
    ret = copy.copy(ns_dict)
    for x in ret:
        ret[x] = copy.copy(ns_dict[x])
    return ret


class Namespace:
    '���ֿռ�'
    def __init__(self,upper = None):
        self.upper = upper
        self.ns = {}
        self.name = "global"

    def get(self, name):
        if name in self.ns:
            return self.ns[name]
        elif self.upper:
            return self.upper.get(name)
        else:
            raise error.NameError(name)

    def __getitem__(self, key):
        return self.get(key)

    def set(self, name, value):
        if name in self.ns:
            raise error.MultipleError(name)
        else:
            self.ns[name] = value

    def __setitem__(self, key, value):
        self.set(key, value)

    def __repr__(self):
        return "Namespace %s" %(self.name)

class Function(Namespace):
    '''����'''
    def __init__(self,name,upper,ret_type = lang.void):
        self.name = name
        self.upper = upper
        self.ns = {}
        self.ret_type = ret_type
        self.params = []
        self.statements = []

    def add_param(self,name,type):
        '�����β�'
        self.params.append(name)
        self.set(name,lang.Object(type))

    def freeze(self):
        '����, ����δ����ǰ�����ֿռ�'
        self.ns_org = copy_ns(self.ns)

    def set_param(self, name, value):
        '����ʵ��'
        if name not in self.ns:
            raise error.NameError(name)
        else:
            self.ns[name].op("assign",value)

    def call(self, args, inter, line_no = None):
        '''�ò���args���ú���,����������Ϊinter'''

        #����ǰ����ѹ�����ջ
        inter.call_stack.append((self, line_no))

        #�����ֳ�
        ns_now = self.ns
        self.ns = copy_ns(self.ns_org)

        old_current = inter.current_ns
        inter.current_ns = self


        ret = lang.Object(lang.void)

        for i in range(len(self.params)):
            self.set_param(self.params[i], args[i])
        for st in self.statements:
            ret = inter.on_statement(st)

        #�ָ��ֳ�
        self.ns = ns_now
        inter.current_ns = old_current

        #����ջ������ǰ����
        inter.call_stack.pop()
        return ret.op("tcast", self.ret_type)

    def __repr__(self):
        return "Function %s " %self.name

class PrintFunc(Function):
    'print ���� ���'
    def __init__(self):
        self.name = "print"

    def call(self,args,inter):
        for x in args:
            x.op("print")
        return lang.Object(lang.void)

class PrintlnFunc(Function):
    'println ���� ���������'
    def __init__(self):
        self.name = "println"

    def call(self,args,inter):
        for x in args:
            x.op("print")
        print
        return lang.Object(lang.void)


inputFlags = {
    "InputBuff" : "",
    "isEOF" : 0
}
class ReadFunc(Function):
    '''read ���� ��������'''
    def __init__(self,input):
        self.name = "read"
        self.input = input
    def call(self,args,inter):
        if self.input["InputBuff"]:
            inp = self.input["InputBuff"]
            try:
                self.input["InputBuff"] = ""
                self.input["InputBuff"] = raw_input()
            except EOFError,e:
                self.input["isEOF"] = 1
        else:
            inp = raw_input()
        return lang.Object(lang.intType, int(inp))


class EofFunc(Function):
    '''eof ����,��������Ƿ����'''
    def __init__(self,input):
        self.name = "eof"
        self.input = input

    def call(self,args,inter):
        if not self.input["InputBuff"] and not self.input["isEOF"]:
            try:
                self.input["InputBuff"] = raw_input()
            except EOFError,e:
                self.input["isEOF"] = 1
        return lang.Object(lang.intType, self.input["isEOF"])


built_in_ns = Namespace()
built_in_ns.ns = {
    'int':lang.intType,
    'void':lang.void,
    'null':lang.null,
    'print':PrintFunc(),
    'println':PrintlnFunc(),
    'read':ReadFunc(inputFlags),
    'eof':EofFunc(inputFlags)
}