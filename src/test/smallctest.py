#coding=utf8
'''Unit Test For interpretor.smallc package'''
import unittest

from test import BaseTestCase, build_test_suit


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(build_test_suit('smallc'))