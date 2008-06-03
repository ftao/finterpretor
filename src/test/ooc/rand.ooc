/*
 * @lang L2
 * @name (伪)随机数生成模块
 * @author Tao Fei (Filia.Tao@gmail.com)
 * @see http://www.vchome.net/tech/datastruct/datasf37.htm
 */

class Rand {
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
			//print(i);
			print(rander.rand());
			println();
			i++;
		)
	}
}

