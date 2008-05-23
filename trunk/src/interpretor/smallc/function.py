#coding=utf8
#$Id$

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
    '名字空间'
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
            raise error.NameReDefineError(name)
        else:
            self.ns[name] = value

    def __setitem__(self, key, value):
        self.set(key, value)

    def __repr__(self):
        return "Namespace %s" %(self.name)

class Function(Namespace):
    '''函数'''
    def __init__(self, name, upper, ret_type = lang.void):
        self.name = name
        self.upper = upper
        self.ns = {}
        self.ret_type = ret_type
        self.params = []
        self.params_type = []
        self.statements = []

    def add_param(self, name, type):
        '增加形参'
        self.params.append(name)
        self.params_type.append(type)
        self.set(name,lang.Object(type))

    def freeze(self):
        '冻结, 备份未调用前的名字空间'
        self.ns_org = copy_ns(self.ns)

    def set_param(self, name, value):
        '设置实参'
        if name not in self.ns:
            raise error.NameError(name)
        else:
            self.ns[name].op("assign", value)

    def call(self, args, inter, line_no = None):
        '''用参数args调用函数,解释器对象为inter'''
        #print "enter function ", self.name
        #将当前函数压入调用栈
        inter.call_stack.append((self, line_no))

        #保存现场
        ns_now = self.ns
        self.ns = copy_ns(self.ns_org)

        old_current = inter.current_ns
        inter.current_ns = self


        ret = lang.Object(lang.void)

        for i in range(len(self.params)):
            self.set_param(self.params[i], args[i])
        for st in self.statements:
            ret = inter.on_statement(st)
            #print "walking statemnt , ", st
            #inter._walk_node(st)
            #ret = inter.action.get_node_attr(st)

        #恢复现场
        self.ns = ns_now
        inter.current_ns = old_current

        #调用栈弹出当前函数
        inter.call_stack.pop()
        return ret.op("tcast", self.ret_type)

    def __repr__(self):
        return "Function %s " %self.name

class PrintFunc(Function):
    'print 函数 输出'
    def __init__(self):
        self.name = "print"
        self.ret_type = lang.void
        
    def call(self, args, inter, line_no = None):
        for x in args:
            print >>io['output'], x.to_str(),
        return lang.Object(lang.void)

class PrintlnFunc(Function):
    'println 函数 输出并换行'
    def __init__(self):
        self.name = "println"
        self.ret_type = lang.void

    def call(self,args,inter, line_no = None):
        for x in args:
            print >>io['output'], x.to_str(),
        print >>io['output']
        return lang.Object(lang.void)


class ReadFunc(Function):
    '''read 函数 读入数据'''
    def __init__(self):
        self.name = "read"
        self.ret_type = lang.intType

    def call(self, args, inter, line_no = None):
        if io["input_buff"]:
            inp = io["input_buff"]
            io["input_buff"] = ""
            while io["input_buff"] == "":
                line = io['input'].readline()
                if line == "":
                    io['is_eof'] = 1
                    break;
                else:
                    io["input_buff"] = line.strip()
        else:
            while True:
                line = io['input'].readline()
                if line == "":
                    raise error.EOFError()
                else:
                    inp = line.strip()
                    if inp != "":
                        break;
        try:
            inp = int(inp)
        except ValueError,e:
            raise error.LangError("Invalid Input")
        return lang.Object(lang.intType, inp)


class EofFunc(Function):
    '''eof 函数,检测输入是否结束'''
    def __init__(self):
        self.name = "eof"
        self.ret_type = lang.intType

    def call(self, args, inter, line_no = None):
        while not io["input_buff"] and not io['is_eof']:
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
