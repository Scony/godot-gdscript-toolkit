func oa(a):
	pass

func x():
	oa(1)

func xx():
	oa(1
		)

func xxx():
	oa(
		1
	)

func xxxx():
	oa(
		1)

func ta(a,b,c):
	pass

func y():
	ta(1,2,3
	)

func yy():
	ta(
		1,
		2,
		3)

func yyy():
	ta(
		1,
		2,
		3
	)

func yyyy():
	ta(
		1,2,3)

func yyyyy():
	ta(
		1,2,3
	)

func z():
	ta(
		1, 2, 3)
	pass

func zz():
	ta(1,2,3)
	pass

var _viewport
func _update_camera_rect(x):
	pass
func foo():
	_update_camera_rect(_update_camera_rect(1))
func _on_camera_update(camera):
	_update_camera_rect(Rect2(
		camera.get_camera_position() + camera.offset \
		- Vector2(_viewport.size.x/2.0, _viewport.size.y/2.0), _viewport.size))
func _on_camera_update2(camera):
	_update_camera_rect(Rect2(
		camera.get_camera_position() + camera.offset \
		- Vector2(_viewport.size.x/2.0, _viewport.size.y/2.0), _viewport.size)
	)
