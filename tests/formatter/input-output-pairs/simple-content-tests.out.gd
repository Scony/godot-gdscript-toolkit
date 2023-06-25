func foo():
	var a = 1 in [1]
	var b = 1 in [1] in [true]
	var c = not 1 in [1] in [true]
	var e = 1 not in [1]
	var f = not 1 not in [1] not in [true]
