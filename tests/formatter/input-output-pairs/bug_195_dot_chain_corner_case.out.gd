func _start_building_placement(building_prototype, Constants):
	var _active_blueprint_node = (
		load(Constants.BUILDING_BLUEPRINTS[building_prototype.resource_path]).instantiate()
	)
