extends Node

func foo():
	var x=1
	var y = x
	var z = 0x99ff
	var q = null
	var w = 'xxx'
	var r = """asd"""
	var t = $Some/Path
	var k = $"../Some/Stuff"
	var l = 0xfF9900
	var m = -0xfF9900
	var b = 0b001101
	var c = -0b001101
	var v=+1
	var n=+x
	var d = ^"../Some/Stuff"
	var e = &"xxx"
	var xa=$%UniqueNodeName
	var xb=$%UniqueNodeName/Xyz
	var xc=%UniqueNodeName
	var xd=%UniqueNodeName/Xyz
	var xe=%"a/b/c"
	var xf=%UniqueNodeName/%AnotherUniqueNodeName
	var xg=$/root
	var xh=$/root/a/b/c
