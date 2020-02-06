extends "simple-class-statements.in.gd"


class C:
	extends "simple-class-statements.in.gd".X


class D:
	extends "simple-class-statements.in.gd".X
	tool


class E:
	extends "simple-class-statements.in.gd"
	tool


class F:
	extends E
	tool


class X:
	class Y:
		tool


class Z:
	extends X.Y
