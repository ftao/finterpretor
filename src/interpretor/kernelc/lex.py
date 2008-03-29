#coding=utf8
#Copyright 2007 Tao Fei (filia.tao@gmail.com)
#Released under GPL V3 (or later)
#see  http://www.gnu.org/copyleft/gpl.html  for more details
import ply.lex as lex


tokens = ('id', 'num',
          'orop','andop','eqop', 'neop', 'ltop', 'gtop', 'leop', 'geop', 'chkop', 'incop', 'decop',
          'kw_func', 'kw_while', 'kw_if', 'kw_else',
          'io_print',
          #'io_println'
          )

literals = ['(', ')', '{', '}', ';', '?', '#', '=', '+', '-', '*', '/', '%' ,'!', '@' ]



t_orop = r'\|\|'

t_andop = r'&&'



t_eqop = r'=='

t_neop = r'!='

t_ltop = r'<'

t_gtop = r'>'

t_leop = r'<='

t_geop = r'>='


t_incop = r'\+\+'

t_decop = r'--'


def t_num(t):
    r'\d+'
    try:
        t.value = int(t.value,10);
    except ValueError:
        print "Number %s is bad!" % t.value
        t.value = 0
    return t


reserved  = {
    "func":    "kw_func",
    "while":   "kw_while",
    "if":      "kw_if",
    "else":    "kw_else",
    "chk":     "chkop",
    "print":   "io_print",
    #"println": "io_println",
    #"read":    "io_read",
    #"eof":     "io_eof"
}

def t_id(t):
    r'\b[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'id')    # Check for reserved words
    return t


def t_newline(t):
    r'\n'
    t.lexer.lineno += 1

t_ignore  = ' \r\t\v'

def t_error(t):
    print "Illegal character '%s' on line %d " % (t.value[0],t.lexer.lineno)
    t.lexer.skip(1)
    lex.has_error = True



# Compute column.
#     input is the input text string
#     token is a token instance
def find_column(input,token):
    i = token.lexpos
    while i > 0:
        if input[i] == '\n': break
        i -= 1
    column = (token.lexpos - i)+1
    return column

test = '''
func gcd {
    chk (*1>1 && *2>1);
    while (*2!=0)
    (
        3=*1%*2;
        1=*2;
        2=*3
    );
    *1
}

func main {

    while (!eof())
    (
        1=read();
        if (!eof())(
            print(*1);
            print(2=read());
            print(gcd())
        )
    )
}
'''

test = '''
func gcd {
    1=*1+*2;
    *1=*2;
    2=4;
    chk (*(*1+1)>1 && *(*1+2)>1);
    while (*(*1+2)!=0)(
        *1+3=*(*1+1)%*(*1+2);
        *1+1=*(*1+2);
        *1+2=*(*1+3)
    );
    3=*(*1+1);
    2=**1;
    1=*1-*2;
    *3
}
func main {
    1=10;
    2=2;
    while (!eof())(
        *1+1=read();
        if (!eof())(
            print(*1+*2+1=*(*1+1));
            print(*1+*2+2=read());
            print(gcd());
            println()
        )
    )
}
'''

lex.lex()

if __name__ == '__main__':
      lexer = lex.lex()
      lexer.input(test)
      while 1:
          tok = lexer.token()
          if not tok: break
          print tok
