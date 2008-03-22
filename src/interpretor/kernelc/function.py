#coding=utf8
'''Kernel C 函数
'''
import sys
import interpretor.kernelc.lang

class Namespace(dict):
    def __getitem__(self, key):
        if key not in self:
            if type(key) == int:
                self[key] = lang.Object(lang.intType)
            else:
                return None #FIXME raise Error?
        return self[key]


class Function:
    def __init__(self, name, statements):
        self.name = name
        self.statements = statements

    def call(self, inter, line_no = None):
        ret = lang.Object(lang.void)
        for st in self.statements:
            ret = inter.on_statement(st)
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



def get_built_in_ns():
    built_in_ns = Namespace()
    built_in_ns.update({
        'read':ReadFunc(),
        'eof':EofFunc()
    })
    return built_in_ns
