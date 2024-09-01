extends Node

func foo():
	$Child
	$"path"
	$'path'
	$"""path"""
	$Child/Sub
	# @"xx"
	# @'xx'
	# @"""xxxx"""
	$Child/Sub.text = "xx"
	$/root
	$/root/A/B/C
