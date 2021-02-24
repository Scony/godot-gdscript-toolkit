extends Node

export var MIN_ROAD_TILES = 100
export var MAX_ROAD_TILES = 1000
export var ROAD_ALTERATION_PROBABILITY = 0.0
export var BUILDING_DENSITY = 0.2
export var DECORATION_DENSITY = 1.0
export var OVERLAY_LAYERS = 2

enum RoadTiles { DEAD_END, STRAIGHT, TURN, T_INTERSECTION, FULL_INTERSECTION }

const TRANSITION_MAP = {
	RoadTiles.DEAD_END: [
		[1.0, RoadTiles.STRAIGHT],
	],
	RoadTiles.STRAIGHT: [
		[0.94, RoadTiles.STRAIGHT],
		[0.03, RoadTiles.FULL_INTERSECTION],
		[0.01, RoadTiles.T_INTERSECTION],
		[0.01, RoadTiles.TURN],
		[0.01, RoadTiles.DEAD_END],
	],
	RoadTiles.TURN: [
		[1.0, RoadTiles.STRAIGHT],
	],
	RoadTiles.T_INTERSECTION: [
		[1.0, RoadTiles.STRAIGHT],
	],
	RoadTiles.FULL_INTERSECTION: [
		[1.0, RoadTiles.STRAIGHT],
	],
}
const ROAD_CONNECTIONS_TO_INDEX_MAPPING = {
	[Vector2(1, 0)]: 104,
	[Vector2(-1, 0)]: 111,
	[Vector2(0, 1)]: 110,
	[Vector2(0, -1)]: 116,
	[Vector2(-1, 0),Vector2(1, 0)]: 73,
	[Vector2(-1, 0),Vector2(0, 1)]: 125,
	[Vector2(-1, 0),Vector2(0, -1)]: 126,
	[Vector2(0, -1),Vector2(0, 1)]: 81,
	[Vector2(0, -1),Vector2(1, 0)]: 124,
	[Vector2(0, 1),Vector2(1, 0)]: 122,
	[Vector2(-1, 0),Vector2(0, -1),Vector2(0, 1),Vector2(1, 0)]: 89,
	[Vector2(-1, 0),Vector2(0, -1),Vector2(1, 0)]: 103,
	[Vector2(-1, 0),Vector2(0, 1),Vector2(1, 0)]: 96,
	[Vector2(-1, 0),Vector2(0, -1),Vector2(0, 1)]: 88,
	[Vector2(0, -1),Vector2(0, 1),Vector2(1, 0)]: 95,
}
const OBJECT_CONNECTIONS_TO_INDEX_MAPPING = {
	[Vector2(1, 0)]: 128 + 1,
	[Vector2(-1, 0)]: 128 + 11,
	[Vector2(0, 1)]: 128 + 2,
	[Vector2(0, -1)]: 128 + 19,
	[Vector2(-1, 0),Vector2(1, 0)]: 67,
	[Vector2(-1, 0),Vector2(0, 1)]: 51,
	[Vector2(-1, 0),Vector2(0, -1)]: 51,
	[Vector2(0, -1),Vector2(0, 1)]: 67,
	[Vector2(0, -1),Vector2(1, 0)]: 51,
	[Vector2(0, 1),Vector2(1, 0)]: 51,
	[Vector2(-1, 0),Vector2(0, -1),Vector2(0, 1),Vector2(1, 0)]: 43,
	[Vector2(-1, 0),Vector2(0, -1),Vector2(1, 0)]: 59,
	[Vector2(-1, 0),Vector2(0, 1),Vector2(1, 0)]: 59,
	[Vector2(-1, 0),Vector2(0, -1),Vector2(0, 1)]: 59,
	[Vector2(0, -1),Vector2(0, 1),Vector2(1, 0)]: 59,
}
const ROAD_CONNECTIONS_TO_ALT_INDEX_MAPPING = {
	[Vector2(-1, 0),Vector2(1, 0)]: [2, 6, 36, 57, 58, 64, 70, 71, 91],
	[Vector2(0, -1),Vector2(0, 1)]: [0, 3, 44, 50, 65, 63, 78, 99],
	[Vector2(-1, 0),Vector2(0, -1),Vector2(0, 1),Vector2(1, 0)]: [82],
}
const BLANK_INDEX = 128 + 129 + 75
const OVERLAY_INDEX = 72
const L_ROT = {
	Vector2(-1, 0): Vector2(0, -1),
	Vector2(0, -1): Vector2(1, 0),
	Vector2(1, 0): Vector2(0, 1),
	Vector2(0, 1): Vector2(-1, 0),
}


class Order:
	static func asc(a, b):
		if a < b:
			return true
		return false


class RoadTile:
	var origin
	var pos
	var type
	var connections
	var index

	func _init(var aOrigin, var aPos, var aType, var aConnections):
		origin = aOrigin
		pos = aPos
		type = aType
		connections = aConnections

	func calculate_index():
		connections.sort_custom(Order, "asc")
		index = ROAD_CONNECTIONS_TO_INDEX_MAPPING[connections]

	func alterate_index(probability):
		connections.sort_custom(Order, "asc")
		if connections in ROAD_CONNECTIONS_TO_ALT_INDEX_MAPPING:
			if randf() < probability:
				var rnd = rand_range(0, len(ROAD_CONNECTIONS_TO_ALT_INDEX_MAPPING[connections]))
				index = ROAD_CONNECTIONS_TO_ALT_INDEX_MAPPING[connections][rnd]


func markovian_tile_type(var tile):
	var possible_transitions = str2var(var2str(TRANSITION_MAP[tile.origin.type])) # wtf
	possible_transitions.sort_custom(Order, "asc")
	if len(possible_transitions) > 1:
		for i in range(1, len(possible_transitions)):
			possible_transitions[i][0] += possible_transitions[i-1][0]
	assert(possible_transitions.back()[0] == 1)
	var random_float = randf()
	for possible_transition in possible_transitions:
		if random_float <= possible_transition[0]:
			tile.type = possible_transition[1]
			break
	assert(len(tile.connections) == 1)
	var origin_connection = tile.connections[0]
	# match tile.type:
	# 	RoadTiles.STRAIGHT:
	# 		tile.connections.append(origin_connection * -1)
	# 	RoadTiles.TURN:
	# 		var new_connections = [L_ROT[origin_connection], L_ROT[origin_connection] * -1]
	# 		new_connections.shuffle()
	# 		new_connections.pop_back()
	# 		tile.connections += new_connections
	# 	RoadTiles.FULL_INTERSECTION:
	# 		tile.connections.append(origin_connection * -1)
	# 		tile.connections.append(L_ROT[origin_connection])
	# 		tile.connections.append(L_ROT[origin_connection] * -1)
	# 	RoadTiles.T_INTERSECTION:
	# 		var new_connections = []
	# 		new_connections.append(origin_connection * -1)
	# 		new_connections.append(L_ROT[origin_connection])
	# 		new_connections.append(L_ROT[origin_connection] * -1)
	# 		new_connections.shuffle()
	# 		new_connections.pop_back()
	# 		tile.connections += new_connections
	return tile


func generate_tbds(var origin_tile):
	var tbds = []
	var origin_connection = origin_tile.origin.pos - origin_tile.pos
	for connection in origin_tile.connections:
		if connection != origin_connection:
			tbds.append(RoadTile.new(origin_tile, origin_tile.pos + connection, null, [connection*-1]))
	return tbds


func _generate_road_map(max_tiles_num):
	var initial_tile = RoadTile.new(null, Vector2(0, 0), RoadTiles.DEAD_END, [Vector2(1, 0)])
	var initial_tbd_tile = RoadTile.new(initial_tile, Vector2(1, 0), null, [Vector2(-1, 0)])
	var established_tiles = {
		initial_tile.pos: initial_tile,
	}
	var tbd_tiles = {
		initial_tbd_tile.pos: initial_tbd_tile,
	}

	var established_tiles_num = 0
	while len(tbd_tiles) > 0 and established_tiles_num < max_tiles_num:
		var tile = markovian_tile_type(tbd_tiles[tbd_tiles.keys()[0]])
		tbd_tiles.erase(tbd_tiles.keys()[0])
		if not tile.pos in established_tiles:
			established_tiles[tile.pos] = tile
			for tbd_tile in generate_tbds(tile):
				if not tbd_tile.pos in tbd_tiles:
					tbd_tiles[tbd_tile.pos] = tbd_tile
				else:
					tile.connections.erase(tbd_tile.pos - tile.pos)
		else:
			established_tiles[tile.pos].connections.erase(tile.origin.pos - tile.pos)
			established_tiles[tile.pos].connections.append(tile.origin.pos - tile.pos)
		established_tiles_num += 1

	# close/merge unfinished paths
	while len(tbd_tiles) > 0:
		var tile = tbd_tiles[tbd_tiles.keys()[0]]
		tbd_tiles.erase(tbd_tiles.keys()[0])
		if not tile.pos in established_tiles:
			established_tiles[tile.origin.pos].connections.erase(tile.pos - tile.origin.pos)
		else:
			established_tiles[tile.pos].connections.erase(tile.origin.pos - tile.pos)
			established_tiles[tile.pos].connections.append(tile.origin.pos - tile.pos)

	# merge dead-ends to neigbours if any
	for pos in established_tiles:
		if len(established_tiles[pos].connections) == 1:
			var pos_to_check = pos + established_tiles[pos].connections[0] * -1
			if pos_to_check in established_tiles:
				established_tiles[pos].connections.append(established_tiles[pos].connections[0] * -1)
				established_tiles[pos_to_check].connections.erase(pos - pos_to_check)
				established_tiles[pos_to_check].connections.append(pos - pos_to_check)

	return [established_tiles, established_tiles_num]


func generate_road_map(min_tiles_num, max_tiles_num):
	var pair = _generate_road_map(max_tiles_num)
	var tiles_num = pair[1]
	while tiles_num < min_tiles_num:
		pair = _generate_road_map(max_tiles_num)
		tiles_num = pair[1]
	var tiles = pair[0]
	return tiles


class ObjectTile:
	var connections
	var index

	func _init(var aConnections):
		connections = aConnections

	func calculate_index(mapping):
		connections.sort_custom(Order, "asc")
		index = mapping[connections]


func generate_object_map(road_tiles, building_density, decoration_density):
	var candidate_tiles = {}
	for pos in road_tiles:
		var missing_connections = [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]
		for connection in road_tiles[pos].connections:
			missing_connections.erase(connection)
		for connection in missing_connections:
			var candidate_pos = pos + connection
			if candidate_pos in road_tiles:
				continue
			if not candidate_pos in candidate_tiles:
				candidate_tiles[candidate_pos] = ObjectTile.new([connection*-1])
			else:
				candidate_tiles[candidate_pos].connections.append(connection*-1)

	var established_tiles = {}
	for pos in candidate_tiles:
		if len(candidate_tiles[pos].connections) == 1 and randf() <= building_density:
			established_tiles[pos] = candidate_tiles[pos]
		elif len(candidate_tiles[pos].connections) != 1 and randf() <= decoration_density:
			established_tiles[pos] = candidate_tiles[pos]
	return established_tiles


func generate_overlay(established_tiles):
	var overlay_tiles = {}
	for pos in established_tiles:
		var directions = [
			Vector2(-1, -1),
			Vector2(-1, 0),
			Vector2(-1, 1),
			Vector2(1, -1),
			Vector2(1, 0),
			Vector2(1, 1),
			Vector2(0, -1),
			Vector2(0, 1),
		]
		for direction in directions:
			var candidate_pos = pos + direction
			if not candidate_pos in established_tiles:
				overlay_tiles[candidate_pos] = true
	return overlay_tiles.keys()


func generate_blanks(established_tiles):
	var blank_tiles = []
	var min_x = 99999
	var max_x = -99999
	var min_y = 99999
	var max_y = -99999
	for pos in established_tiles:
		if pos.x < min_x:
			min_x = pos.x
		if pos.x > max_x:
			max_x = pos.x
		if pos.y < min_y:
			min_y = pos.y
		if pos.y > max_y:
			max_y = pos.y
	assert(min_x < max_x)
	assert(min_y < max_y)
	for x in range(min_x, max_x):
		for y in range(min_y, max_y):
			if not Vector2(x, y) in established_tiles:
				blank_tiles.append(Vector2(x, y))
	return blank_tiles


func generate_tile_map():
	var tiles = {}
	var road_tiles = generate_road_map(MIN_ROAD_TILES, MAX_ROAD_TILES)
	for pos in road_tiles:
		road_tiles[pos].calculate_index()
		road_tiles[pos].alterate_index(ROAD_ALTERATION_PROBABILITY)
		tiles[pos] = road_tiles[pos].index
	var object_tiles = generate_object_map(road_tiles, BUILDING_DENSITY, DECORATION_DENSITY)
	for pos in object_tiles:
		object_tiles[pos].calculate_index(OBJECT_CONNECTIONS_TO_INDEX_MAPPING)
		tiles[pos] = object_tiles[pos].index
	for i in range(0, OVERLAY_LAYERS):
		for pos in generate_overlay(tiles):
			tiles[pos] = OVERLAY_INDEX
	for pos in generate_blanks(tiles):
		tiles[pos] = BLANK_INDEX
	return tiles


func setup_tile_map(tiles):
	for pos in tiles:
		$Navigation2D/TileMap.set_cellv(pos, tiles[pos])


func init():
	randomize()
	setup_tile_map(generate_tile_map())
	# comment with trailing ws 
