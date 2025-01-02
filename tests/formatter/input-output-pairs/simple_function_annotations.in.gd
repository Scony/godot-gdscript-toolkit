func a():
	@warning_ignore("unused_variable")
	var x: Array[int] = [ 1, 2, ]

func b():
	@warning_ignore("unused_variable") var x: Array[int] = [ 1, 2, ]

func d():
	@warning_ignore("unused_variable") @warning_ignore("unused_variable") var x: Array[int] = [ 1, 2, ]

@warning_ignore("unused_parameter")
func e():
	@warning_ignore("unused_variable")
	@warning_ignore("unused_variable")
	var x: Array[int] = [ 1, 2, ]

func f():
	if true:
		@warning_ignore("unused_variable")
		@warning_ignore("unused_variable")
		var x: Array[int] = [ 1, 2, ]

func g():
	@warning_ignore("unused_variable")

func h():
	if true:
		@warning_ignore("unused_variable")

@rpc
func i():
	pass

@rpc("any_peer", "call_local")
func j():
	pass
