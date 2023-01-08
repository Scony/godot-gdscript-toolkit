class X:
	func foo():
		var x = [  # a
			1,  # b
			2,  # c
		]  # d
		var y = {  # q
			"x": 1,  # w
			"y": 2,  # e
		}  # r
		var sut
		var Config
		(
			sut
			. init(
				self,
				{
					0: "x",
					1: "y",
					2: "z",
				},
				{
					Config.Household.LevelingDirection.POSITIVE: 0.1,  # 10%/s
					Config.Household.LevelingDirection.NEGATIVE: 0.1,
				}
			)
		)
		sut.process(10.0, 0)  # 0.0
