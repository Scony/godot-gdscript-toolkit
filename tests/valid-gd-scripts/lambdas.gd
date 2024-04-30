extends Node

func _ready():
	var l1 = func(x): pass;print('l1', x)
	l1.call('foo')
	var ls = [func(): print('l3'), func(): print('l4')]
	ls[1].call()
	var lss = [
	func(): print('l6')]
	lss[1].call()
	get_tree().process_frame.connect(func(): pass;print('x'))
