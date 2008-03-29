#coding=utf8
'''Kernel C 函数
'''
import sys
import interpretor.kernelc.lang as lang

class Namespace(dict):
    def __getitem__(self, key):
        if not self.has_key(key):
            if type(key) is int:
                self[key] = lang.Object(lang.intType, 0, True) # is left value
            else:
                return None #FIXME raise Error?

        return dict.__getitem__(self ,key)



class Function:
    def __init__(self, name, statements):
        self.name = name
        self.statements = statements

    def call(self, inter, line_no = None):
        ret = lang.Object(lang.void)
        for st in self.statements:
            ret = inter.on_statement(st)
        return ret

    def __str__(self):
        return "\n".join([str(st) for st in self.statements])

    __repr__ = __str__

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

class PrintlnFunc(Function):
    'println 函数 换行'
    def __init__(self):
        self.name = "println"

    def call(self,inter, line_no = None):
        print >>io['output']


class ReadFunc(Function):
    '''read 函数 读入数据'''
    def __init__(self):
        self.name = "read"
    def call(self, inter, line_no = None):
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

    def __str__(self):
        return "read"

    __repr__ = __str__

class EofFunc(Function):
    '''eof 函数,检测输入是否结束'''
    def __init__(self):
        self.name = "eof"

    def call(self, inter, line_no = None):
        while not io["input_buff"] and not io['is_eof']:
            line = io['input'].readline()
            if line == "":
                io['is_eof'] = 1
            else:
                io["input_buff"] = line.strip()

        return lang.Object(lang.intType, io["is_eof"])

    def __str__(self):
        return "eof"

    __repr__ = __str__

def get_built_in_ns():
    built_in_ns = Namespace()
    built_in_ns.update({
        'read':ReadFunc(),
        'eof':EofFunc(),
        'println':PrintlnFunc(),
    })
    return built_in_ns
