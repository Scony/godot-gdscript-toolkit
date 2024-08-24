# GDScript Toolkit
[![](https://github.com/Scony/godot-gdscript-toolkit/workflows/Tests/badge.svg?branch=master)](https://github.com/Scony/godot-gdscript-toolkit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This project provides a set of tools for daily work with `GDScript`. At the moment it provides:

- A parser that produces a parse tree for debugging and educational purposes.
- A linter that performs a static analysis according to some predefined configuration.
- A formatter that formats the code according to some predefined rules.
- A code metrics calculator which calculates cyclomatic complexity of functions and classes.

## Installation

To install this project you need `python3` and `pip`.
Regardless of the target version, installation is done by `pip3` command and for stable releases, it downloads the package from PyPI.

### Godot 4

```
pip3 install "gdtoolkit==4.*"
# or
pipx install "gdtoolkit==4.*"
```

### Godot 3

```
pip3 install "gdtoolkit==3.*"
# or
pipx install "gdtoolkit==3.*"
```

### `master` (latest)

Latest version (potentially unstable) can be installed directly from git:
```
pip3 install git+https://github.com/Scony/godot-gdscript-toolkit.git
# or
pipx install git+https://github.com/Scony/godot-gdscript-toolkit.git
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

## Calculating cyclomatic complexity with gdradon

To run cyclomatic complexity calculator you need to execute the `gdradon` command like:

```
gdradon cc tests/formatter/input-output-pairs/simple-function-statements.in.gd tests/gd2py/input-output-pairs/
```

The command outputs calculated metrics just like [Radon cc command](https://radon.readthedocs.io/en/latest/commandline.html#the-cc-command) does for Python code:
```
tests/formatter/input-output-pairs/simple-function-statements.in.gd
    C 1:0 X - A (2)
    F 2:1 foo - A (1)
tests/gd2py/input-output-pairs/class-level-statements.in.gd
    F 22:0 foo - A (1)
    F 24:0 bar - A (1)
    C 18:0 C - A (1)
tests/gd2py/input-output-pairs/func-level-statements.in.gd
    F 1:0 foo - B (8)
```

## Using gdtoolkit's GitHub action

In order to setup a simple action with gdtoolkit's static checks, the base action from this repo can be used:

```
name: Static checks

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  static-checks:
    name: 'Static checks'
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: Scony/godot-gdscript-toolkit@master
    - run: gdformat --check source/
    - run: gdlint source/
```

See the discussion in https://github.com/Scony/godot-gdscript-toolkit/issues/239 for more details.

## Development [(more)](https://github.com/Scony/godot-gdscript-toolkit/wiki/5.-Development)

Everyone is free to fix bugs or introduce new features. For that, however, please refer to existing issue or create one before starting implementation.
