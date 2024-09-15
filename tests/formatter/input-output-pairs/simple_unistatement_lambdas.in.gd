func foo():
	var x1 = func(): pass
	var x2 = func() -> int: return 1
	var x3 = func baz() -> int: return 1
	var x5 = func(): 1
	var x6 = func baz(): pass
	var x7 = func(): var x
	var x8 = func(): var x=1
	var x9 = func(): var x:int
	var x10 = func(): var x:int=1
	var x11 = func(): var x:=1
	var x12 = func(): breakpoint
	var x13 = func(): const foo =1
	var x13a = func(): const foo:int =1
	var x13b = func(): const foo:=1
	# TODO: fix
	# var x14 = func(): if true: pass
	# var x15 = func(): while false: pass
	# var x16 = func(): for x in [1]: pass
	# var x17 = func(): for x : int in [1]: pass
	pass

func bar():
	var x1 = func():
		pass
	var x2 = func() -> int:
		return 1
	var x3 = func baz() -> int:
		return 1
	var x5 = func():
		1
	var x6 = func baz():
		pass
	var x7 = func():
		var x
	var x8 = func():
		var x=1
	var x9 = func():
		var x:int
	var x10 = func():
		var x:int=1
	var x11 = func():
		var x:=1
	var x12 = func():
		breakpoint
	var x13 = func():
		const foo =1
	var x13a = func():
		const foo:int =1
	var x13b = func():
		const foo:=1
	var x14 = func():
		if true:
			pass
	var x15 = func():
		while false:
			pass
	var x16 = func():
		for x in [1]:
			pass
	var x17 = func():
		for x : int in [1]:
			pass
	var x18 = func():
		match 1:
			_:
				pass
	pass
