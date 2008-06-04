#coding=utf8
#$Id$

'''Unit Test For interpretor.ooc package'''
import unittest
from test import BaseTestCase, build_test_suit

def filter(f):
    #return True
    return f.find("sp") != -1

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity = 2).run(build_test_suit('ooc', filter))