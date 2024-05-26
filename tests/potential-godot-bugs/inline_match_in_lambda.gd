func foo():
	var x1 = func(): if true: pass # this works
	var x2 = func(): match 1: _: pass # this doesn't
