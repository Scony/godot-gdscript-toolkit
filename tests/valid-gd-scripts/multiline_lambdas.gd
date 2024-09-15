func foo():
	var f0 = func bar():
		pass
	var f1 = func():
		pass
	var f11 = func():
		var f11r = func():
			pass
	var f12 = func():
		var f12r = func():
			return func(): pass
	var f13 = func():
		pass
		var f13r = func():
			pass
			return func(): pass
	var f14 = func():
		pass
		var f14r = func():
			if true:
				pass
	var f15 = func():
		pass
		var f15r = func():
			if true:
				pass
			pass
		pass
	var f16 = func():
		@warning_ignore("unused_variable")
	var f17 = func():
		@warning_ignore("unused_variable")
		var x
	var f18 = func():
		@warning_ignore("unused_variable") var x
	var f19 = func():
		@warning_ignore("unused_variable") @warning_ignore("unused_variable") var x
	var f2s = [func():
		pass
	]
	var f3s = [func():
		pass
		pass
	]
	var f4s = [func():
		pass]
	var f5s = [func():
		pass
		pass]
	var f6s = [func():
		pass, func():
		pass]
	var f7s = [func():
		return [1,2,3], func():
		pass]
	var f8s = [func():
		pass
		var f8sr = func():
			pass
			var dct = {'f':func():
				pass
				var f8srr = func():
					pass
					return [1,2,3]}]
	# Godot 4.3 failing:
	# var fx = func():
	# 	pass if true else func():
	# 	pass
	# var fx = func():
	# 	pass is int
