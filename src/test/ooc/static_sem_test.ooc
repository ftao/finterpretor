/*
 * @lang L2
 * @name 静态语义测试
 * @author Tao Fei (Filia.Tao@gmail.com)
 */

class Rand {
    const
    MIN = 1, MAX = 999;

    static
    var int count end

    private
    var int next end

    public
    func Rand constructor(int seed){
        this.srand(seed);
        this;
    }

    func int srand(int seed){
        this.next = seed;
    }

    func int rand(){
        this.next = this.next * 1103515245 + 12345;
        (this.next / 65536) % 32768;
    }

}

class Main{
    static
    func void main(){
        var int i,num,seed;Rand rander end
        num = 100;
        seed = 8799;
        i = 1;
        rander = new Rand.constructor(seed);
        while( i < num)
        (
            print(i);
            print(rander.rand());
            println();
            i++;
        )
    }

    public
    func int test(Object obj){
        var int i, j; int[] ar,br; Rand r end
        i + j;
        i / j;
        i + ar;
        i * ar;
        r == null;
        r != ar;
        ar == r;
        obj != r;
        ar == obj;
        ar[obj];
        ar.length > 3;
        r.length;
        r * 4;
        Rand.MIN * Rand.MAX;
        Rand.MIN_MAX;
        r.MAX + r.MIN;
        r.MIN = 4;
        i = main();
        i = test77();
        j = test();
        j = test(r);
        j = test(4);
        j = test(ar);
        j = test(r, r);
    }
}

