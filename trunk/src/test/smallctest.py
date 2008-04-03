#coding=utf8
'''Unit Test For interpretor.smallc package'''
import unittest
import sys
import os
import glob
import StringIO
import interpretor.smallc.interp as interp



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
        for src_file in glob.glob('./smallc/*.src'):
            if os.path.isfile(src_file):
                code = open(src_file).read()
                try:
                    input_file = open(src_file[:src_file.rfind('.')] + '.in')
                except IOError,e:
                    input_file = sys.stdin
                try:
                    expect_out = open(src_file[:src_file.rfind('.')] + '.out').read()
                except IOError,e:
                    expect_out = ""
                print "Current File : %s" %(src_file,)
                out = run_and_get_output(code,input_file)
                self.assertEqual(out,expect_out)
                print "OK"



class BadSourceTest(unittest.TestCase):
    pass



if __name__ == "__main__":
    unittest.main()