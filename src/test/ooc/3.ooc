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
