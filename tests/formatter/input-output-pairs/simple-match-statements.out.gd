class X:
	func foo(x):
		match x:
			1:
				pass
			1, 2:
				pass
			"x":
				pass
			Vector2.ZERO.x:
				pass
			{"a": 1, "b": 2}:
				pass
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
