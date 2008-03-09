#coding=gbk
import copy
import sys
import interpretor.smallc.lang as lang
import interpretor.smallc.error as error

def copy_ns(ns_dict):
    ret = copy.copy(ns_dict)
    for x in ret:
        ret[x] = copy.copy(ns_dict[x])
    return ret

io = {
    'input' : sys.stdin,
    'output' : sys.stdout,
    'input_buff' : "",
    'is_eof' : 0
}


def set_io(input_f,output_f):
    io['input'] = input_f
    io['output'] = output_f
    io['input_buff'] = ""
    io['is_eof'] = 0

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
    def __init__(self, name, upper, ret_type = lang.void):
        self.name = name
        self.upper = upper
        self.ns = {}
        self.ret_type = ret_type
        self.params = []
        self.statements = []

    def add_param(self, name, type):
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
            self.ns[name].op("assign", value)

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

    def call(self, args, inter, line_no = None):
        for x in args:
            print >>io['output'], x.to_str(),
        return lang.Object(lang.void)

class PrintlnFunc(Function):
    'println ���� ���������'
    def __init__(self):
        self.name = "println"

    def call(self,args,inter, line_no = None):
        for x in args:
            print >>io['output'], x.to_str(),
        print >>io['output']
        return lang.Object(lang.void)


class ReadFunc(Function):
    '''read ���� ��������'''
    def __init__(self):
        self.name = "read"
    def call(self, args, inter, line_no = None):
        if io["input_buff"]:
            inp = io["input_buff"]
            io["input_buff"] = ""
            line = io['input'].readline()
            if line == "":
                io['is_eof'] = 1
            else:
                io["input_buff"] = line.strip()
        else:
            line = io['input'].readline()
            if line == "":
                raise error.EOFError()
            else:
                inp = line.strip()
        try:
            inp = int(inp)
        except ValueError,e:
            raise error.LangError()
        return lang.Object(lang.intType, inp)


class EofFunc(Function):
    '''eof ����,��������Ƿ����'''
    def __init__(self):
        self.name = "eof"

    def call(self, args, inter, line_no = None):
        if not io["input_buff"] and not io['is_eof']:
            line = io['input'].readline()
            if line == "":
                io['is_eof'] = 1
            else:
                io["input_buff"] = line.strip()
        return lang.Object(lang.intType, io["is_eof"])

def get_built_in_ns():
    built_in_ns = Namespace()
    built_in_ns.ns = {
        'int':lang.intType,
        'void':lang.void,
        'null':lang.null,
        'print':PrintFunc(),
        'println':PrintlnFunc(),
        'read':ReadFunc(),
        'eof':EofFunc()
    }
    return built_in_ns