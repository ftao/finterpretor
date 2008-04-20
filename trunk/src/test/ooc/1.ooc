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