#coding=utf8
'''
测试用公共函数
'''
import re
import StringIO
import unittest
class TestHelper():
    def __init__(self, engine, source, input, expect):
        '''source , input， expect 可以是类文件对象或者字符串'''
        self.engine = engine
        self.source = source
        self.input = input
        self.expect = expect

    def check_num_value_same(self, result , expect):
        '所有数据值得比较，忽略其他'
        #'忽略分割符(空格，逗号，回车)的比较'
        tidy_result = re.findall('\d+', result, re.MULTILINE)
        tidy_except = re.findall('\d+', expect, re.MULTILINE)
        return tidy_result == tidy_except

    def check_output(self):
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
        return self.check_num_value_same(output_stream.getvalue(), expect)


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

