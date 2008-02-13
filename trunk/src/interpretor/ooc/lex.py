#coding=gbk
#Copyright 2007 Tao Fei (filia.tao@gmail.com)
#Released under GPL V3 (or later)
#see  http://www.gnu.org/copyleft/gpl.html  for more details
import ply.lex as lex


tokens = ('id', 'num',
          'orop','andop','eqop', 'neop', 'ltop', 'gtop', 'leop', 'geop', 'chkop', 'incop', 'decop',
          'kw_class', 'kw_const', 'kw_var', 'kw_end', 'kw_func', 'kw_while', 'kw_if', 'kw_else', 'kw_new',
          "kw_abstract","kw_private","kw_public","kw_redef","kw_static")

literals = ['{', '}', ';', ",", "[", "]", '(', ')', '=', '+', '-', '*', '/', '%' ,'!', '@' ,'.', '?', ':']

#t_assignop = r'='
#
#t_addop = r'+'
#
#t_minusop = r'-'
#
#t_mulop = r'*'
#
#t_divop = r'/'
#
#t_modop = r'%'
#
#t_notop = r'!'


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
    "class":   "kw_class",
    "const":   "kw_const",
    "var":     "kw_var",
    "end":     "kw_end",
    "func":    "kw_func",
    "while":   "kw_while",
    "if":      "kw_if",
    "else":    "kw_else",
    "new":     "kw_new",
    "static":  "kw_static",
    "private": "kw_private",
    "public":  "kw_public",
    "abstract":"kw_abstract",
    "redef":   "kw_redef",
    "chk":     "chkop"
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
 class abstract Node { public func abstract int target() func abstract int subnodenum()
   func abstract Node down(int) func abstract void output(int) }
 class abstract Mono:Node { public func abstract Node up() }
 class Backtracking { private var Mono prob; int num, bound end
 public func Backtracking constructor(Mono p, int b){ prob=p; bound=b; this }
   func void depthfirst(){ var int m, i end  m=prob.subnodenum(); i=0;
     if (prob.target())( prob.output(1); ++num);
     while (num<bound && i<m)
       if (prob.down(i++)!=null)( depthfirst(); prob.up()) } }
 class Queens:Mono { private var int n, level; int[] board, column, d1, d2 end
 public func Queens constructor(int k){ n=k; board=new int[n];
     column=new int[n]; d1=new int[2*n-1]; d2=new int[2*n-1]; this }
 redef func int target(){ level==n }
   func int subnodenum(){ if (level<n) n else 0 }
   func Node down(int i){ var Queens ans; int norm, k end ans=null;
     if (level<n && !column[i] && !d1[level+i] && !d2[level-i+n-1])(
       column[i]=1; d1[level+i]=1; d2[level-i+n-1]=1;
       board[level++]=i; ans=this); ans }
   func Node up(){ var int i end
     i=board[--level]; column[i]=0; d1[level+i]=0; d2[level-i+n-1]=0; this }
   func void output(int b){ var int i end
     if (level==n)( i=0; while (i<n) print(board[i++]); println() ) } }
 class Main { static func void main(){
     new Backtracking.constructor(new Queens.constructor(8), 1).depthfirst() } }
'''

lex.lex()

if __name__ == '__main__':
      lexer = lex.lex()
      lexer.input(test)
      while 1:
          tok = lexer.token()
          if not tok: break
          print tok
