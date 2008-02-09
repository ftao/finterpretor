#coding=gbk
#Copyright 2007 Tao Fei (filia.tao@gmail.com)
#Released under GPL V3 (or later)
#see  http://www.gnu.org/copyleft/gpl.html  for more details
import ply.lex as lex


tokens = ('id', 'num',
          'orop','andop','eqop', 'neop', 'ltop', 'gtop', 'leop', 'geop', 'chkop', 'incop', 'decop',
          'kw_class', 'kw_const', 'kw_var', 'kw_end', 'kw_func', 'kw_while', 'kw_if', 'kw_else', 'kw_new')

literals = ['{', '}', ';', ",", "[", "]", '(', ')', '=', '+', '-', '*', '/', '%' ,'!', '@' ,'.', '?']

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

test1 = '''
 func void main(){ var int i, j end
   print(2);
   read();
   i = 0;
   while(i < 1)(i++;print(i))
   }
'''
test = '''
 class Link { Node prob; Link next }
 class Node { int level; int[] board }
 func void main(){ var int i, j; Link a; Node b end
     b.board = new int[2];
     b.board[1] = 2;
     b.board[0] = 3;
     print (b.board[0]);
     print (b.board[1]);
     b.level = 1;
     print(b.level)
    }
'''
test = '''
 func int gcd(int a, int b){ var int r end
   chk (a>1 && b>1);
   while (b!=0)(r=a%b; a=b; b=r);
   a }
 func void main(){ var int i, j end
   while (!eof())( i=read();
     if (!eof())( j=read();
       println(i, j, gcd(i, j)))) }
'''

test3 = '''
 class Link { Node prob; Link next }
 class Node { int level; int[] board }
 const n=8;
 var Link head; int num, bound end
 func void depthfirst(){ var Link t; Node p, sub; int m, i end
   p=head.prob; sub=null; m=subnodenum(p); i=0;
   if (target(p))( outlist(head); ++num );
   while (num<bound && i<m)
     if ((sub=down(p, i++))!=null)( t=new Link; t.prob=sub;
       t.next=head; head=t; depthfirst(); head=head.next ) }
 func int subnodenum(Node this){ if (this.level<n) n else 0 }
 func int target(Node this){ this.level==n }
 func Node down(Node this, int i){ var Node ans; int norm; int k end
   ans=null; norm=this.level<n; k=this.level-1;
   while (norm && k>=0)(
     norm=i!=this.board[k] && i+this.level-k!=this.board[k]
          && i-this.level+k!=this.board[k]; --k );
   if (norm)( this.board[this.level]=i; ans=new Node;
     ans.level=this.level+1; ans.board=new int[ans.level+1];
     k=0; while (k<ans.level)( ans.board[k]=this.board[k]; ++k ) ); ans }
 func void outlist(Link this){
   if (this.next!=null) outlist(this.next); outnode(this.prob) }
 func void outnode(Node this){ var int i end
   if (this.level==n)( i=0; while (i<n) print(this.board[i++]); println() ) }
 func void main(){ bound=1; head=new Link; head.prob=new Node;
   head.prob.board=new int[1]; depthfirst() }
'''
lex.lex()

if __name__ == '__main__':
      lexer = lex.lex()
      lexer.input(test)
      while 1:
          tok = lexer.token()
          if not tok: break
          print tok
