#coding=gbk
'''
解释器Shell
可以加载两个不同的引擎,来解释不同的语言
'''
import sys

sys.path.insert(0,"..")

class Shell:

    def __init__(self,name,engineer):
        self.code = ""
        self.engineer = engineer
        self.name = "L"

    def start(self):
        print self.name , "shell 0.1"
        print "type help for help"
        self.run()

    def run(self):
        while(True):
            command = ""
            try:
                command = raw_input(">>>")
            except EOFError,e:
                continue
            if command.startswith("clear"):
                self.clear()
            elif command.startswith("read"):
                self.read()
            elif command.startswith("load"):
                filename = eval(command.split()[1])
                self.load(filename)
            elif  command.startswith("exit"):
                self.exit()
            elif command.startswith("help"):
                self.help()
            elif command == "":
                pass
            else:
                print "error command"



    def clear(self):
        self.code = ""

    def read(self):
        self.clear()
        try:
            while(True):
                self.code += raw_input() + '\n'
        except EOFError,e:
            pass
        print self.code
        self.engineer.run(self.code)

    def exit(self):
        sys.exit()

    def help(self):
        print "supported commands:"
        print "  read : read from stdin and run the code (using CTRL+Z(Windows) or CTRL+D(*nix)"
        print "  load : load from file and run the code "
        print "  exit : eixt"
        print "  clear: clear"
        print "  help : show this message"

    def load(self,filename):
        self.code = open(filename).read()
        self.engineer.run(self.code)
        self.clear()

if __name__ == '__main__':
    import  interpretor.smallc.interp as engieer
    Shell("L1",engieer).start()