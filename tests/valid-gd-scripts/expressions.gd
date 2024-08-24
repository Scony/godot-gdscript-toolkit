extends Node

enum Xyz { AAA }

const XXXX = preload('functions.gd')

class Zyx:
	enum Qwe { BBB }

class XNode extends Node:
	class YNode extends Node:
		pass

func bar():
	pass

func foo():
	var x
	1 if true else 2
	1 or 2
	1 || 2
	1 and 3
	1 && 3
	not 5
	! 5
	5 in x
	1 > 2
	1 < 2
	1 == 2
	1 != 1
	1 >= 12
	2 <= 43
	3 | 3
	6 ^ 5
	8 & 7
	5 >> 7
	7 << 5
	5 - 6
	6 + 7
	7 * 7
	7 / 8
	6 % 3
	-8
	~8
	5 ** 5
	x is int
	x is not int
	x is Xyz # TODO: fix/remove x.Type
	x is Zyx.Qwe # TODO: fix/remove x.Type
	x.attr
	x[10]
	bar()
	(2+2)
	var xxxx = XXXX.new()
	xxxx.fun(1, 2)
	x[1][2][3]['xxx'][1+2]
	x[1] += 2
	x[1] ^= 2
	x[1] >>= 2
	x[1] <<= 2
	x[1] **= 2
	x.bar()[1]
	x.attr = 34
	1_000_000 > 0
	1_000.000 > 0.0
	0xff_99_00 > 0
	x as XNode.YNode
	x as XNode . YNode

class Foo:
	pass
