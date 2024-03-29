/**
 * @lang L2
 * @name S先生与P先生谜题
 * @author Tao Fei (Filia.Tao@gmail.com)
 */

class Main {

	const MIN = 2, MAX = 99;

	//只需要判断y的范围, 程序确保x的取值范围
	static
    func int BaseCondition(int x, int y)
	{
		y >= MIN && y <= MAX && y >= x
	}

	//S先生的S分析
	func int[][] S(int x, int y)
	{
		var int[][] ar; int s,i,len end
	    s = x + y;
	    len = s/2 + 1 - MIN;
	    ar = new int[][len];
	    i = 0;
	    while(i < len)
	    (
	    	ar[i] = new int[2];
	    	ar[i][0] = i + MIN;
	    	ar[i][1] = s - i - MIN;
	    	i++
	    );
	    ar
	}

	//P先生的P分析
	func int[][] P(int x, int y)
	{
		var int[][] ar; int p,i,len end
	    p = x * y;
	    i = MIN;
	    len = 0;
	    while( i <= p/i)
	    (
	    	if (p % i == 0 &&  BaseCondition(i, p/i))
	    		len ++;
            i ++
	    );
	    ar = new int[][len];
	    i = MIN;
        len = 0;
	    while( i <= p/i)
	    (
            if (p % i == 0 &&  BaseCondition(i, p/i))
	    	(
                ar[len] = new int[2];
                ar[len][0] = i;
                ar[len][1] = p/i;
                len ++
            );
	    	i++
	    );
	    ar
	}

    //条件1 - S：我确信你不知道这两个数是什么，但我也不知道
    func int Condition1(int x, int y)
    {
        var int[][] s_sep; int i,ret end
        s_sep = S(x, y);

        ret = 1;
        if (s_sep.length == 1)
        (
            ret = 0
        )
        else
        (
            i = 0;
            while (ret && i < s_sep.length)
            (
                if (P(s_sep[i][0], s_sep[i][1]).length <= 1)
                    ret = 0;

                i++
            )
        );
        ret
    }

    //条件2 - P: 一听你说这句话，我就知道这两个数是什么了
    func int Condition2(int x, int y)
    {
        var int[][] p_sep; int i,ret end
        p_sep = P(x,y);
        i = 0 ;
        ret = 1;
        while (ret && i < p_sep.length )
        (
            if (x == p_sep[i][0] && y == p_sep[i][1])
            (
                 ret
            )
            else
            (
                if (Condition1(p_sep[i][0], p_sep[i][1]))
                (

                    ret = 0
                 )
            );
            i++
        );
        ret
    }

    //条件3 - S: 我也是，现在我也知道了。
    func int Condition3(int x, int y)
    {
        var int[][] s_sep; int i,ret end
        s_sep = S(x,y);
        i = 0 ;
        ret = 1;
        while (ret && i < s_sep.length)
        (
            if (x == s_sep[i][0] && y == s_sep[i][1])
            (
                ret
            )
            else
            (
                if (Condition2(s_sep[i][0], s_sep[i][1]))
                    ret = 0
            );
            i++
        );
        ret
    }

    //需要同时满足上面3个条件
    func int Condition(int x, int y)
    {
        Condition1(x, y ) &&  Condition2(x, y) && Condition3(x, y)
    }

    func void main()
    {
        var int i,j,x,y end

        i = MIN;
        x = 0;
        y = 0;
        while ( i <= MAX && x == 0 && y == 0)
        (
            j = i;
            while(j < MAX && x == 0 && y == 0)
            (
	            //print (i);
	            //println (j);
                if(Condition(i,j))
                (
                    x = i;
                    y = j
                );
                j++
            );
            i ++
        );
        print (x);
        print (y);
    }

}

/*
以下内容来自：
http://hyry.dip.jp/blogt.py?file=0200.blog
我用OOC 语言实现 S先生与P先生谜题, 大体框架使用下面的文章中的内容
****************************************************************
这道题目来自美国斯坦福大学的麦卡锡教授----S先生与P先生谜题。

题目：S先生与P先生谜题

设有两个自然数X、Y，2<=X<=Y<=99,S先生知道这两个数的和S，P先生知道这两个数的积P，他们二人进行了如下对话：

    * S：我确信你不知道这两个数是什么，但我也不知道。
    * P: 一听你说这句话，我就知道这两个数是什么了。
    * S: 我也是，现在我也知道了。

现在你能通过他们的会话推断出这两个数是什么吗？（当然，S和P先生都是非常聪明的）

关于这道题目的解题思路可以参考： Prolog教程S先生与P先生

*/
