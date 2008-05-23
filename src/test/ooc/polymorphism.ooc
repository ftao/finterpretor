/*
 * @lang L2
 * @name 多态测试
 * @author Tao Fei (Filia.Tao@gmail.com)
 */


class A{
    public 
    func void some_method()
    {
        //do something for A
        print (1)
    }
}

class B:A{
    redef 
    func void some_method()        
    {
        //do something different for B
        print (2)
    }
    func void another_method() //should report error ,but not yet ... FIXME 
    {
        print (1);
    }
}

class Main{
    static func void main()
    {
        var A a; B b end
        a = new A;
        a.some_method(); //will print 1
        b = new B;
        a = b;
        a.some_method(); //will print 2 
        b.some_method(); //will print 2
        a:A.some_method(); //will print 1  强制类型转换,按转换后类型处理
    }
}

