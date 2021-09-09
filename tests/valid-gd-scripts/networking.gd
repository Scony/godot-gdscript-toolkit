remote func foo():
	return null

remotesync func bar():
	return null

master func baz():
	return null

mastersync func baz_sync():
	return null

puppet func asd():
	return null

puppetsync func asd_sync():
	return null

sync func qwe():
	return null

puppet var x
puppet var xx = 1
puppet var xxx : int
puppet var xxxx : int = 1
puppet var xxxxx := 1

# TODO: check if empty export (working w/ Godot 3.3.2) makes any sense
# export puppet var y

export puppet var yy = 1
export puppet var yyy : int
export puppet var yyyy : int = 1
export puppet var yyyyy := 1

export (int) puppet var zz = 1
export (int) puppet var zzz : int
export (int) puppet var zzzz : int = 1
export (int) puppet var zzzzz := 1
