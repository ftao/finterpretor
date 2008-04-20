#coding=utf8
'''
测试用公共函数
'''
import re
import StringIO
import unittest
import glob
import os
import sys

class BaseTestCase(unittest.TestCase):

    def __init__(self, engine, source, input, expect):
        '''source , input， expect 可以是类文件对象或者字符串'''
        self.engine = engine
        self.source = source
        self.input = input
        self.expect = expect
        super(BaseTestCase, self).__init__()

    def assert_num_value_same(self, result , expect):
        '所有数据值得比较，忽略其他'
        #'忽略分割符(空格，逗号，回车)的比较'
        tidy_result = re.findall('\d+', result, re.MULTILINE)
        tidy_except = re.findall('\d+', expect, re.MULTILINE)
        self.assertEqual(tidy_result, tidy_except)

    def runTest(self):
        '''测试输出结果是否和预期相同'''
        if type(self.source) is str:
            code = self.source
        else:
            code = self.source.read()
        if type(self.input) is str:
            input_stream = StringIO.StringIO(self.input)
        else:
            input_stream = self.input
        if type(self.expect) is str:
            expect = self.expect
        else:
            expect = self.expect.read()
        output_stream = StringIO.StringIO()
        self.engine.run(code, input_stream, output_stream)
        self.assert_num_value_same(output_stream.getvalue(), expect)

def build_test_suit(lang, filter_func = None):
    interp = __import__('interpretor.%s.interp' %(lang), fromlist = ['interpretor' ,lang])
    suite = unittest.TestSuite()
    subfix = lang[0:2] + lang[-1] #kec smc ooc
    source_file_list = glob.glob('./%s/*.%s' %(lang,subfix))
    for src_file in source_file_list:
        if filter_func is not None:
            if not filter_func(src_file):
                continue
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
