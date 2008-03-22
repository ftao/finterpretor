#coding=utf8
class ParseError(Exception):

    def __init__(self,token):
        self.token = token

    def __str__(self):
        return "Parser error at line %d token '%s'"  %(self.token.lineno, self.token.value)


class LangError(Exception):

    def __init__(self, msg = ""):
        self.msg = msg

    def __str__(self):
        return "Language Error : %s" %self.msg

class NotLeftValueError(LangError):
    pass


class ChkFailError(LangError):
    def __str__(self):
        return "Chk failed"

class UnsupportedOPError(LangError):
    def __init__(self,op):
        self.op = op

    def __str__(self):
        return "unsupported operation '%s'" %(self.op)