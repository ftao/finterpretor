/*
 * @lang L2
 * @name 面向对象测试 
 * @author Tao Fei (Filia.Tao@gmail.com)
 */

class A {
    const c_1 = 100;

    static 
    var int sta_a_1; int[] sta_a_2 end
    func int s_method(int arg)
    {
        sta_a_1 = arg; 
        sta_a_2 = new int[2];
        sta_a_2[0] = arg;
        sta_a_2[1] = 2*arg; 
        arg
    }
     
    private 
    var int pr_a_1; int [] pr_a_2 end
    func int pr_method(int arg)
    {
        pr_a_1 = arg * 2;
        pr_a_2 = new int[3];
        pr_a_2[0] = arg;
        pr_a_2[1] = arg * 2;
        pr_a_2[2] = arg * 4;
    }

    public
    var int pub_a_1; int[] pub_a_2 end
    func int p_method(int arg)
    {
        pub_a_1 = arg/2;
        pub_a_2 = new int[2];
        pub_a_2[0] = arg;
        pub_a_2[1] = 2*arg
    }
}


class Main{
    
    static 
    func void main()
    {
        var A a end
        a = new A; 
        print (a.c_1);
        print (A.c_1);
        println(); 

        print (a.s_method(11));
        print (a.sta_a_1);
        print (A.sta_a_1);
        print (A.sta_a_2);
        println(); 

        //the following report error 
        //print (a.pr_method(22));
        //print (a.pr_a_1);
        //print (a.pr_a_2);
        println(); 

        print (a.p_method(33));
        print (a.pub_a_1);
        print (a.pub_a_2);
        println(); 
   }
}

