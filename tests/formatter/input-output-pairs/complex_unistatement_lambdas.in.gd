func foo(x):
	pass
func bar(x,y):
	pass

func baz():
	foo(func(): pass)
	bar(func(): pass,func(): pass)
	var x1 = [func(): pass,func(): pass]
	var x2 = [func(): pass,func():pass,]
	var x3 = {'x':func(): pass,'y':func(): pass}
	var x4 = {'x':func(): pass,'y':func(): pass,}
