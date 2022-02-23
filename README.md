# GDScript Toolkit
[![](https://github.com/Scony/godot-gdscript-toolkit/workflows/Tests/badge.svg?branch=master)](https://github.com/Scony/godot-gdscript-toolkit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This project provides a set of tools for daily work with `GDScript`. At the moment it provides:

- A parser that produces a parse tree for debugging and educational purposes.
- A linter that performs a static analysis according to some predefined configuration.
- A formatter that formats the code according to some predefined rules.

## Installation

To install this project you need `python3` and `pip`. 

Use this command in your terminal to install from PyPI repository:

```
pip3 install 'gdtoolkit==3.*'
```

Alternatively, you can install latest (potentially unstable) version directly from git:
```
pip3 install git+https://github.com/Scony/godot-gdscript-toolkit.git
```

## Linting with gdlint [(more)](https://github.com/Scony/godot-gdscript-toolkit/wiki/3.-Linter)

To run a linter you need to execute `gdlint` command like:

```
$ gdlint misc/MarkovianPCG.gd
```

Which outputs messages like:

```
misc/MarkovianPCG.gd:96: Error: Function argument name "aOrigin" is not valid (function-argument-name)
misc/MarkovianPCG.gd:96: Error: Function argument name "aPos" is not valid (function-argument-name)
```

## Formatting with gdformat [(more)](https://github.com/Scony/godot-gdscript-toolkit/wiki/4.-Formatter)

**Formatting may lead to data loss, so it's highly recommended to use it along with Version Control System (VCS) e.g. `git`**

To run a formatter you need to execute `gdformat` on the file you want to format. So, given a `test.gd` file:

```
class X:
	var x=[1,2,{'a':1}]
	var y=[1,2,3,]     # trailing comma
	func foo(a:int,b,c=[1,2,3]):
		if a in c and \
		   b > 100:
			print('foo')
func bar():
	print('bar')
```

when you execute `gdformat test.gd` command, the `test.gd` file will be reformatted as follows:

```
class X:
	var x = [1, 2, {'a': 1}]
	var y = [
		1,
		2,
		3,
	]  # trailing comma

	func foo(a: int, b, c = [1, 2, 3]):
		if a in c and b > 100:
			print('foo')


func bar():
	print('bar')
```

## Parsing with gdparse [(more)](https://github.com/Scony/godot-gdscript-toolkit/wiki/2.-Parser)

To run a parser you need to execute the `gdparse` command like:

```
gdparse tests/valid-gd-scripts/recursive_tool.gd -p
```

The parser outputs a tree that represents your code's structure:

```
start
  class_def
    X
    class_body
      tool_stmt
      signal_stmt	sss
  class_def
    Y
    class_body
      tool_stmt
      signal_stmt	sss
  tool_stmt
```

## Running tests

To run tests you need [tox](https://tox.readthedocs.io/en/latest/), a tool to automate testing in Python.

Install it with:

```
pip3 install tox
```

To invoke entire test suite, in the `godot-gdscript-toolkit` project directory, run:

```
tox
```

You can run only selected test cases:

```
tox -e py3 -- -k lint
```

For manual testing, you can consider installing package in editable mode:

```
pip3 install -e .
```
