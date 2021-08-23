extends Node

func foo():
	123
	"asdf"
	3.1415926
	58.1e-10
	'asdf'
	"""single line"""
	"""x"x"""
	# @"asdf/dfg"
	$Node
	$"../xxx"
	0xaf01
	0xAfA01
	0b0101111
	012
	null

func assert_string_contains(text, search, match_case=true):
	var empty_search = "Expected text and search strings to be non-empty. You passed \"%s\" and \"%s\"."
	var disp = "Expected \"%s\" to contain \"%s\", match_case=%s" % [text, search, match_case]

func assert_string_contains2(text, search, match_case=true):
	var empty_search = 'Expected text and search strings to be non-empty. You passed \'%s\' and \'%s\'.'
	var disp = 'Expected \'%s\' to contain \'%s\', match_case=%s' % [text, search, match_case]


const GREETING = """Hello Merchant!
Welcome to the first tutorial.
My name is Siegfried and I'll assist you throughout the game.
In this tutorial, I'll walk you through the basic game mechanics.
Go ahead and click "Next" to start."""
