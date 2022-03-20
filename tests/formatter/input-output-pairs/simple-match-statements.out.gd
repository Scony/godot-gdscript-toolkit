class X:
	func foo(x):
		match x:
			1:
				pass
			1, 2:
				pass
			"x":
				pass
			x:
				pass
			x.aaa.bbb:
				pass
			[1, 2,]:
				pass
			{"a": 1, "b": 2}:
				pass
			# TODO: verify on 4.0
			# {a = 1, b = 2}:
			# 	pass
			# {"a": 1, b = 2}:
			# 	pass
			[1, ..]:
				pass
			var a:
				pass
			(1):
				pass
			~1:
				pass
			-1:
				pass
			+1:
				pass
			1 * 1:
				pass
			1 + 1:
				pass
			1 << 1:
				pass
			1 & 1:
				pass
			1 ^ 1:
				pass
			1 | 1:
				pass
			1 > 1:
				pass
			not 1:
				pass
			1 and 2:
				pass
			1 or 2:
				pass
			1 if 1 else 2:
				pass
			_:
				pass
		match Vector3(1, 1, 1):
			Vector3(1, 1 + 1, 1):
				pass
