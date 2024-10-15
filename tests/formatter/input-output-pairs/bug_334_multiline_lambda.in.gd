class WeaponSystemBullet extends Node:
	pass
func foo():
	var bullet_scene
	assert(
		(func() -> bool:
			var test_instance: Node = bullet_scene.instantiate()
			var is_needed_class: bool = test_instance is WeaponSystemBullet
			test_instance.free()
			return is_needed_class)
		.call()
	)
