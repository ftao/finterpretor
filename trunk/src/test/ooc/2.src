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