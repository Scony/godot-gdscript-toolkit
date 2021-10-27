extends Node

func coroutine():
	print('coroutine(): 1 #', get_tree().get_frame())
	await get_tree().process_frame
	print('coroutine(): 2 #', get_tree().get_frame())
	await get_tree().process_frame
	print('coroutine(): 3 #', get_tree().get_frame())
	return 1


func fw_coroutine():
	print('fw_coroutine(): 1 #', get_tree().get_frame())
	var x = int(await coroutine() is int) + 1
	print(x)
	print('fw_coroutine(): 2 #', get_tree().get_frame())
	
	
func coroutine2():
	print('coroutine2(): 1 #', get_tree().get_frame())
	await get_tree().process_frame
	print('coroutine2(): 2 #', get_tree().get_frame())
	await get_tree().process_frame
	print('coroutine2(): 3 #', get_tree().get_frame())
	return get_tree().process_frame


func fw_coroutine2():
	print('fw_coroutine2(): 1 #', get_tree().get_frame())
	await await coroutine2()
	print('fw_coroutine2(): 2 #', get_tree().get_frame())
	
	
func _ready():
	print('_ready(): 1 #', get_tree().get_frame())
	fw_coroutine()
	fw_coroutine2()
	print('_ready(): 2 #', get_tree().get_frame())

# outcome:

# _ready(): 1 #0
# fw_coroutine(): 1 #0
# coroutine(): 1 #0
# fw_coroutine2(): 1 #0
# coroutine2(): 1 #0
# _ready(): 2 #0
# coroutine(): 2 #8
# coroutine2(): 2 #8
# coroutine(): 3 #9
# 2
# fw_coroutine(): 2 #9
# coroutine2(): 3 #9
# fw_coroutine2(): 2 #9
