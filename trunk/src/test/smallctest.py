#coding=utf8
'''Unit Test For interpretor.smallc package'''
import unittest
import sys
import os
import glob
import interpretor.smallc.interp as interp
from test import TestHelper,BaseTestCase

def infile_to_outfile(infile):
    return infile[:infile.rfind('.')] + '.out'

class GoodSourceTest(unittest.TestCase):
    test_lang = "smallc"

    def setUp(self):
        if 'source_file_list' in globals():
            self.source_file_list = globals()['source_file_list']
        else:
            self.source_file_list = glob.glob('./%s/*.src' %(self.test_lang))

    def test_all(self):
        print "runing "
        print "get test files from folder 'smallc'"
        prefix = ''
        for src_file in self.source_file_list:
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
                test_helper = TestHelper(interp, code, input_file, expect_out)
                self.assertTrue(test_helper.check_output())
                print "OK"

def build_test_suit():
    suite = unittest.TestSuite()
    source_file_list = glob.glob('./%s/*.src' %('smallc'))
    for src_file in source_file_list:
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
            test  = BaseTestCase(interp, code, input_file, expect_out)
            #test.config(interp, code, input_file, expect_out)
            suite.addTest(test)
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity = 2).run(build_test_suit())