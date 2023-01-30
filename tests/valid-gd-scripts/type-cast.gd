enum Named { Foo, Bar = 1 if true else 0 }


func foo(x):
	return x


func bar():
	foo(1 as int)
	var x = [1 as int, 2, 3]
	x[1 as int]
	var y = {
		1 as int: 1 as int,
	}
	var z = {
		x = 1 as int,
	}
	print(1.5 as int)
