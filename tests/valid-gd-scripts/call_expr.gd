func bar():
	pass

func foo():
	var xxx
	bar()
	.foo(1,2,3)
	xxx.aaa()
	xxx.yyy.aaa()
	xxx[0].aaa()
	xxx[0].yyy[1].aaa()
	xxx.yyy[0].aaa()
	bar().xxx[0].aaa()
