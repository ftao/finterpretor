#coding=utf8
#$Id$
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
        self.name = name
        self.recent_command = []
        self.version = "0.1"
    def start(self):
        print self.name , "shell ", self.version
        print "type help for help"
        self.run()

    def run(self):
        while(True):
            command = ""
            try:
                command = raw_input(">>>")
            except EOFError,e:
                print "Please use 'exit' to exit the shell"
                continue
            if command:
                self.recent_command.append(command)
                self.on_command(command)


    def on_command(self,command):
        if command.startswith("clear"):
            self.clear()
        elif command.startswith("read"):
            self.read()
        elif command.startswith("load"):
            try:
                filename = command.split()[1]
                if filename[0] == '"' and filename[-1] == '"':
                    filename = filename[1:-1]
            except (IndexError),e:
                print "bad argument for load command"
                return
            self.load(filename)
        elif  command.startswith("exit"):
            self.exit()
        elif command.startswith("help"):
            self.help()
        elif command.startswith("list"):
            for i in range(len(self.recent_command)):
                print "%d : %s" %(i+1, self.recent_command[i])
            print "using exec <number> to exec recent command"
        elif command.startswith("exec"):
            try:
                number = int(command.split()[1])
            except (IndexError,ValueError),e:
                print "bad argument for exec command"
                return
            try:
                self.on_command(self.recent_command[number-1])
            except IndexError,e:
                print "No command with id %d" %(number,)
        else:
            print "error command"
    def clear(self):
        self.code = ""

    def read(self):
        self.clear()
        while(True):
            try:
                self.code += raw_input()
            except EOFError,e:
                break
        if self.code:
            self.engineer.run(self.code)

    def exit(self):
        sys.exit()

    def help(self):
        print self.name , "shell ", self.version
        print "Author: TaoFei (Filia.Tao@gmail.com)"
        print "supported commands:"
        print "  clear : clear"
        print "  exit : eixt"
        print "  exec <command-id>: execute recent command"
        print "  help : show this message"
        print "  list : list recent commands"
        print "  load <filename> : load from file and run the code "
        print "  read : read from stdin and run the code"
        print "         using CTRL+Z+Return(Windows) or CTRL+D(*nix) to finish the input"



    def load(self,filename):
        try:
            self.code = open(filename).read()
        except IOError,e:
            print "cann't load file '%s'" %(filename)
            return
        self.engineer.run(self.code)

if __name__ == '__main__':
    if len(sys.argv) <= 1 or sys.argv[1] not in ["L1", "L2"]:
        print "Plase choose a engieer"
        print "L0, L1 , L2 "
        print "eg: %s L1" %(sys.argv[0])
    else:
        if sys.argv[1] == "L1":
            import  interpretor.smallc.interp as engieer
        elif sys.argv[1] == "L2":
            import  interpretor.ooc.interp as engieer
        shell = Shell(sys.argv[1],engieer)
        if len(sys.argv) > 2:
            shell.load(sys.argv[2])
        else:
            shell.start()

