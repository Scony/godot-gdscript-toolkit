extends "res://tests/formatter/input-output-pairs/nested-classes.in.gd"

class C:
	extends "res://tests/formatter/input-output-pairs/nested-classes.in.gd".X

class D extends "res://tests/formatter/input-output-pairs/nested-classes.in.gd".X:
	pass

class E extends "res://tests/formatter/input-output-pairs/nested-classes.in.gd":
	pass

class F extends E:
	pass

class X:
	class Y:
		pass

class Z:
	extends X.Y
