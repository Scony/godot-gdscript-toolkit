extends "res://dummy.gd"


class C:
	extends "res://dummy.gd".X


class D:
	extends "res://dummy.gd".X
	pass


class E:
	extends "res://dummy.gd"
	pass


class F:
	extends E
	pass


class G:
	class Y:
		pass


class Z:
	extends G.Y
