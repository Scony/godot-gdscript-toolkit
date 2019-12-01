extends Node

func foo():
	123
	"asdf"
	3.1415926
	58.1e-10
	'asdf'
	"""single line"""
	@"asdf/dfg"
	$Node
	$"../xxx"

func assert_string_contains(text, search, match_case=true):
	var empty_search = "Expected text and search strings to be non-empty. You passed \"%s\" and \"%s\"."
	var disp = "Expected \"%s\" to contain \"%s\", match_case=%s" % [text, search, match_case]

func assert_string_contains2(text, search, match_case=true):
	var empty_search = 'Expected text and search strings to be non-empty. You passed \'%s\' and \'%s\'.'
	var disp = 'Expected \'%s\' to contain \'%s\', match_case=%s' % [text, search, match_case]
