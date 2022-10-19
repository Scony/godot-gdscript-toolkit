func foo():
	var x1 = func(): pass
	var x2 = func(x): pass;pass
	var x3 = func(x: int): return 123;pass
	var x4 = func bar(): pass;123
	var x5 = func() -> int: 1
	var x6 = func baz() -> int: pass
	var x7 = func(): var x
	var x8 = func(): var x=1
	var x9 = func(): var x:int
	var x10 = func(): var x:int=1
	var x11 = func(): var x:=1
