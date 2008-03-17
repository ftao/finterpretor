#coding=utf8

from interpretor.ast import Node,Leaf

#build in functions
def bif_print(z):
    print z,

def bif_println(z):
    print z

def bif_read():
    pass

def bif_eof():
    pass

class Interpreter:

    def __init__(self,ast):
        self.ast = ast

        self.functions = {           # Built-in function table
            'print'   : bif_print,
            'println' : bif_println,
            'read'    : bif_read,
            'eof'     : bif_eof
        }


    def run(self):
        pass