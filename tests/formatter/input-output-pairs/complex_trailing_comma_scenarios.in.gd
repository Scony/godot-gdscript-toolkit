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
