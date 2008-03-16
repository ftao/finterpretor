#coding=utf8
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


# Comments
def t_comment1(t):
    r'//.*'
    pass

def t_comment2(t):
    r'/\*(.|\n)*?\*/'
    t.lineno += t.value.count('\n')


def t_error(t):
    print "Illegal character '%s' on line %d " % (t.value[0],t.lexer.lineno)
#    t.lexer.skip(1)
#    lex.has_error = True



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
 public func Backtracking constructor(Mono p, int b){prob=p;bound=b; this }
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

test = '''
 class abstract Node { public func abstract int target()
   func abstract int subnodenum()
   func abstract Node down(int)
    func abstract void output(int)  }
  class Back { private var Link head; int num, bound end
  public func Back constructor(Node p, int b){
      head=new Link.constructor(p, null); bound=b; this }
    func void depthfirst(){ var Node p, sub; int m, i end
      p=head.prob; m=p.subnodenum(); i=0;
     if (p.target())( head.output(1); ++num);
     while (num<bound && i<m)
     if ((sub=p.down(i++))!=null)(
       head=new Link.constructor(sub, head); depthfirst(); head=head.next) } }
 class Link { public var Node prob; Link next end
   func Link constructor(Node p, Link n){ prob=p; next=n; this }
   func void output(int b){ if (next!=null) next.output(0); prob.output(b) } }
 class Queens:Node { const n=8;
 private var int level; int[] board end
 public func Queens constructor1(){ board=new int[1]; this }
   func Queens constructor2(int lev, int[] b){ var int k end
     level=lev; board=new int[level+1];
     k=0; while (k<level)( board[k]=b[k]; ++k); this }
 redef func int target(){ level==n }
   func int subnodenum(){ if (level<n) n else 0 }
   func Node down(int i){ var Queens ans; int norm, k end
     norm=level<n; k=level-1; ans=null;
     while (norm && k>=0)( norm=i!=board[k] && i+level-k!=board[k] && i-level+k!=board[k]; --k );
       if (norm)( board[level]=i; ans=new Queens.constructor2(level+1, board) ); ans }
   func void output(int b){ var int i end  if (level==n)( i=0; while (i<n) print(board[i++]); println() ) } }
 class Main { static func void main(){
   new Back.constructor(new Queens.constructor1(), 1).depthfirst() } }
'''

test = '''
/* class abstract */
/*
mulit line
comment


*/
 class abstract Node { public func abstract int target()    // comment end line
   func abstract int subnodenum() func abstract Node down(int)
   func abstract void output(int)  }
 class LabelBack { private var Link head; int num, bound; Set nodeset end
 public func LabelBack constructor(Node p, int b, Set s){
     head=new Link.constructor(p, null);
     bound=b; nodeset=s; nodeset.add(p); this }
   func void depthfirst(){ var Node p, sub; int m, i end
     p=head.prob; m=p.subnodenum(); i=0;
     if (p.target())( head.output(1); ++num);
     while (num<bound && i<m)
       if ((sub=p.down(i++))!=null && !nodeset.contains(sub))(
         head=new Link.constructor(sub, head); nodeset.add(sub);
         depthfirst(); head=head.next; nodeset.remove(sub)) } }
 class Link { public var Node prob; Link next end
   func Link constructor(Node p, Link n){ prob=p; next=n; this }
   func void output(int b){ if (next!=null) next.output(0); prob.output(b) } }
 class abstract Set { public func abstract int contains(Object)
   func abstract void add(Object) func abstract void remove(Object) }
 class abstract PairNode:Node { public func abstract int tag1()
   func abstract int tag2() }
 class Knight:PairNode { static var int m, n; int[][] move, board end
 private var int x, y, level end
 public func Knight constructor1(int mm, int nn, int[][] mov){
   var int i end m=mm; n=nn; move=mov; level=1;
     board=new int[][m]; i=0; while (i<m) board[i++]=new int[m]; this }
   func Knight constructor2(int lev, int xx, int yy){ level=lev; x=xx; y=yy; this }
 redef func int target(){ level==m*m }
   func int subnodenum(){ if (level<m*m) n else 0 }
   func Node down(int i){ var int x1, y1 end x1=x+move[i][0]; y1=y+move[i][1];
     if (x1>=0 && x1<m && y1>=0 && y1<m)
       new Knight.constructor2(level+1, x1, y1) else null }
   func void output(int b){ var int i, j end board[x][y]=level;
     if (level==m*m)( i=0;
       while (i<m)( j=0;
         while (j<m)( print(board[i][j]); ++j); println(); ++i)) }
   func int tag1(){ x }   func int tag2(){ y } }
 class Bmatrix:Set { private var int[][] set end
 public func Bmatrix constructor(int row, int column) { var int i end
     set=new int[][row]; i=0; while (i<row) set[i++]=new int[column]; this }
 redef func int contains(Object o){ var int k1, k2 end
     k1=o:PairNode.tag1(); k2=o:PairNode.tag2();
     k1>=0 && k1<set.length && k2>=0 && k2<set[k1].length && set[k1][k2] }
   func void add(Object o){ var int k1, k2 end
     k1=o:PairNode.tag1(); k2=o:PairNode.tag2();
     if (k1>=0 && k1<set.length && k2>=0 && k2<set[k1].length) set[k1][k2]=1 }
   func void remove(Object o){ var int k1, k2 end
     k1=o:PairNode.tag1(); k2=o:PairNode.tag2();
     if (k1>=0 && k1<set.length && k2>=0 && k2<set[k1].length) set[k1][k2]=0 } }
 class Main {
 static func void main(){ var int n, i; int[][] move; Set nset end n=5;
   nset=new Bmatrix.constructor(n, n); move=new int[][8];
   i=0; while (i<8) move[i++]=new int[2]; move[0][0]=2; move[0][1]=1; move[1][0]=1; move[1][1]=2;
   move[2][0]=-1; move[2][1]=2; move[3][0]=-2; move[3][1]=1; move[4][0]=-2; move[4][1]=-1;
   move[5][0]=-1; move[5][1]=-2; move[6][0]=1; move[6][1]=-2; move[7][0]=2; move[7][1]=-1;
   new LabelBack.constructor(new Knight.constructor1(n, 8, move), 1, nset).depthfirst() } }
'''

lex.lex()

if __name__ == '__main__':
      lexer = lex.lex()
      lexer.input(test)
      while 1:
          tok = lexer.token()
          if not tok: break
          print tok
