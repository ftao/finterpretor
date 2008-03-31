#coding=utf8
'''Unit Test For interpretor.kernelc package'''
import unittest
import sys
import os
import glob
import StringIO
import interpretor.kernel.interp as interp

'''
= 怎样用L0语言编程 =
可以看出L0 语言是一种很低级的语言。由于没有局部变量，要非常小心处理变量，可以在这里把变量作为寄存器来想像。为了编程方便,我自己在编程过程中使用了如下规则.
  * 约定函数的参数使用的变量，不重复(一般从1开始编号即可)
  * 函数内部使用的局部变量使用
'''

def run_and_get_output(code,infile):
    outp = StringIO.StringIO()
    interp.run(code, infile, outp)
    return outp.getvalue()

def infile_to_outfile(infile):
    return infile[:infile.rfind('.')] + '.out'

class GoodSourceTest(unittest.TestCase):
    def test_all(self):
        print "runing "
        print "get test files from folder 'smallc'"
        prefix = ''
        for src_file in glob.glob('./kernelc/*.src'):
            if os.path.isfile(src_file):
                code = open(src_file).read()
                input_file = open(src_file[:src_file.rfind('.')] + '.in')
                expect_out = open(src_file[:src_file.rfind('.')] + '.out').read()
                print "Current File : %s" %(src_file,)
                out = run_and_get_output(code,input_file)
                self.assertEqual(out,expect_out)
                print "OK"



class BadSourceTest(unittest.TestCase):
    pass



if __name__ == "__main__":
    unittest.main()