# GDScript Toolkit
[![](https://travis-ci.com/Scony/godot-gdscript-toolkit.svg?branch=master)](https://travis-ci.com/Scony/godot-gdscript-toolkit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This project provides a set of tools for daily work with `GDScript`. At the moment it provides:

- A parser that produces a parse tree for debugging and educational purposes.
- A linter that performs a static analysis according to some predefined configuration.
- A formatter that formats the code according to some predefined rules.

## Installation

To install this project you need `python3` and `pip`. 

Use this command in your terminal to install from this git repository:

```
pip3 install gdtoolkit
```

## Linting with gdlint

To run a linter you need to perform installation first. Once done, you can run e.g.:

```
$ gdlint misc/MarkovianPCG.gd
```

Which outputs messages like:

```
misc/MarkovianPCG.gd:96: Error: Function argument name "aOrigin" is not valid (function-argument-name)
misc/MarkovianPCG.gd:96: Error: Function argument name "aPos" is not valid (function-argument-name)
```

To tweak the default check settings, you can dump the default config to a file:

```
$ gdlint -d
$ cat gdlintrc
class-load-variable-name: (([A-Z][a-z0-9]*)+|_?[a-z][a-z0-9]*(_[a-z0-9]+)*)
class-name: ([A-Z][a-z0-9]*)+
class-variable-name: _?[a-z][a-z0-9]*(_[a-z0-9]+)*
constant-name: '[A-Z][A-Z0-9]*(_[A-Z0-9]+)*'
disable: []
enum-element-name: '[A-Z][A-Z0-9]*(_[A-Z0-9]+)*'
enum-name: ([A-Z][a-z0-9]*)+
function-argument-name: _?[a-z][a-z0-9]*(_[a-z0-9]+)*
function-arguments-number: 10
function-load-variable-name: ([A-Z][a-z0-9]*)+
function-name: (_on_([A-Z][a-z0-9]*)+(_[a-z0-9]+)*|_?[a-z][a-z0-9]*(_[a-z0-9]+)*)
function-variable-name: '[a-z][a-z0-9]*(_[a-z0-9]+)*'
load-constant-name: (([A-Z][a-z0-9]*)+|[A-Z][A-Z0-9]*(_[A-Z0-9]+)*)
loop-variable-name: _?[a-z][a-z0-9]*(_[a-z0-9]+)*
signal-name: '[a-z][a-z0-9]*(_[a-z0-9]+)*'
sub-class-name: _?([A-Z][a-z0-9]*)+
```

Once the dump is performed, you can modify the `gdlintrc` file and optionally rename it to `.gdlintrc`.
From now on, linter will use this config file to override the default config.

## Formatting with gdformat

**Formatting may lead to data loss, so it's highly recommended to use it along with Version Control System (VCS) e.g. `git`**

`gdformat` is the uncompromising GDScript code formatter. The only configurable thing is max line length allowed (`--line-length`). The rest will be taken care of by `gdformat` in a one, consistent way.

To run a formatter you need to perform installation first. Once done, given a `test.gd` file:

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

when you run `gdformat test.gd`, the `test.gd` file will be reformatted as follows:

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

If the program formats your files successfully, it will return the exit code `0`. Non-zero code will be returned otherwise.

## Parsing with gdparse

To parse a file, use the `gdparse` program:

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

If the program parses your file sucessfully, it will return the exit code `0`.

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
