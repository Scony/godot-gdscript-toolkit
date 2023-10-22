extends Node

func coroutine(_r):
	await get_tree().process_frame
	return 1

func coroutine2():
	await get_tree().process_frame
	return get_tree().process_frame

func foo():
	await get_tree().process_frame
	var x=int(await coroutine([]) is int)+1
	var y = [1,await coroutine([1,2,]),]
	await await coroutine2()
