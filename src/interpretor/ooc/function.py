#coding=utf8
import copy
import interpretor.ooc.lang as lang
import interpretor.ooc.error as error

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
    '''名字空间。 出现ID时从名字空间中获得对应的对象
    实际上只有一个全局名字空间是这个类的实例。其他都是对应子类的实例。
    '''
    def __init__(self, upper=None):
        self.upper = upper #上级名字空间？
        self.ns = {}
        self.name = "global"

    def get(self, name):
        "取得name 对应的对象"
        if name in self.ns:
            return self.ns[name][0]
        elif self.upper:
            return self.upper.get(name)
        else:
            raise error.NameError(name)

    def __getitem__(self, key):
        return self.get(key)

    def set(self, name, value, decorate = None):
        "将名字加入到名字空间,检查重复定义"
        if name in self.ns:
            raise error.MultipleError(name)
        else:
            self.ns[name] = (value,decorate)

    def __repr__(self):
        return "Namespace %s" %(self.name)

    __str__ = __repr__

class Function(Namespace):
    '''函数。 Namespace 的子类。
    OOC 语言中的函数都属于某一个类
    名字，对应类，返回类型，修饰符(public,static,redef等）
    参数有add_param 方法增加
    TODO: abstract 的问题？
    '''
    def __init__(self,name,cls,ret_type, decorate):
        self.name = name
        self.params = []
        self.ns = {}
        self.cls = cls
        self.ret_type = ret_type
        self.decorate = decorate
        self.obj = None  #调用函数的对象。

    def add_param(self,name,type):
        '增加一个参数'
        self.params.append(name)
        self.set(name,lang.Object(type))

    def freeze(self):
        '函数定义完成后,冻结这个函数'
        self.ns_org = copy_ns(self.ns)

    def set_param(self, name, value):
        '''函数调用时，设置参数的值'''
        if name not in self.ns:
            raise NameError(name)
        else:
            self.ns[name].op("assign",value)  #注意这里，使用op_assign来设置参数可保证语义正确

    def get(self, name):
        '''取得name 对应的对象
         函数中访问一个名字，来源可能有：
         函数名字空间，实例变量，类变量，类方法，全局名字
        '''
        if name in self.ns:
            return self.ns[name]
        else:
            if self.decorate == "static":#如果调用的静态方法
                #类静态变量，对全局名字空间的访问包含在这个调用中，下同。
                return self.cls.op_get_cls(name)
            else:
                if name == "this":   #对于this 特殊处理
                    return self.obj
                #通过实例可以访问的变量。包括实例变量和类变量
                return self.obj.op("get", name)


    def set(self, name, value):
        '增加名字。函数自己的名字空间中没有修饰符的区别'
        if name in self.ns:
            raise MultipleError(name)
        else:
            self.ns[name] = value

    def call(self, obj, args, inter, line_no = None):
        '在obj 上调用本函数，参数为args, 解释器对象是inter'

        #print "calling func %s in obj %s with args %s" %(self.name,obj,args)
        #将当前函数压入调用栈
        inter.call_stack.append((self, line_no))

        #下面三个是现场保护， 名字空间字典,调用对象，解释器但前名字空间
        ns_now = self.ns
        #这里的copy_ns 是一个半深半浅的复制
        self.ns = copy_ns(self.ns_org)

        old_obj = self.obj
        self.obj = obj

        old_current = inter.current_ns
        inter.current_ns = self


        for i in range(len(self.params)):
            self.set_param(self.params[i], args[i])
        for st in self.statements:
            ret = inter.on_statement(st)

        #恢复现场
        self.ns = ns_now
        inter.current_ns = old_current
        self.obj = old_obj

        #调用栈弹出当前函数
        inter.call_stack.pop()

        #转换成返回类型
        return ret.op("tcast", self.ret_type)

    def __repr__(self):
        return "Function %s " %self.name

    __str__ = __repr__

class AbstractFunction(Function):
    def __init__(self,name,cls,ret_type, decorate):
        self.name = name
        self.params = []
        self.cls = cls
        self.ret_type = ret_type
        self.decorate = decorate

    def call(self,obj,args,inter):
        '试图调用abstract 函数时，引发一个异常'
        raise error.UnimplementedMethodError(self.name , self.cls.name)


#下面是几个内置函数，或者说是操作符。
class PrintFunc(Function):
    def __init__(self):
        self.name = "print"

    def call(self,obj,args,inter,line_no):
        for x in args:
            print >>io['output'], x.to_str(),
        return lang.Object(lang.void)

    def __repr__(self):
        return "function %s" %(self.name)

class PrintlnFunc(Function):
    def __init__(self):
        self.name = "println"

    def call(self,obj,args,inter,line_no):
        for x in args:
            print >>io['output'], x.to_str(),
        print >>io['output']
        return lang.Object(lang.void)




class ReadFunc(Function):
    def __init__(self):
        self.name = "read"
        self.input = input
    def call(self,obj,args,inter,line_no):
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
    def __init__(self,input):
        self.name = "eof"
        self.input = input
    def call(self,obj,args,inter,line_no):
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
        'int': (lang.intType,"builtin"),
        'void': (lang.void,"builtin"),
        'null': (lang.null,"builtin"),
        'print': ((PrintFunc(),None),"builtin"),
        'println': ((PrintlnFunc(),None),"builtin"),
        'read': ((ReadFunc(inputFlags),None),"builtin"),
        'eof': ((EofFunc(inputFlags),None),"builtin"),
        'Object': (lang.rootClass,"builtin")
    }
    return built_in_ns
