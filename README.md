# GDScript Toolkit
[![](https://travis-ci.org/Scony/godot-gdscript-toolkit.svg?branch=master)](https://travis-ci.org/Scony/godot-gdscript-toolkit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This project aims to create an end-to-end set of tools for daily work with `GDScript`. The goal is to provide the following tools:

- A parser that produces a parse tree for debugging and educational purposes.
- A compiler to create an easy to use Intermediate Representation of the code (IR).
- A linter that performs a static analysis according to some predefined configuration.
- A formatter to format the code according to some predefined rules.

## Current progress

The parser and the language grammar are ready to use, although they may have minor bugs. If you find any, please [open an issue](https://github.com/Scony/godot-gdscript-toolkit/issues/new).

The linter is currently a work-in-progress, however, some useful tests are already available.

The formatter is close to being complete, however, it's still a work-in-progress.

## Installation

To install this project you need `python3` and `pip`. 

Use this command in your terminal to install from this git repository:

```
pip3 install git+https://github.com/Scony/godot-gdscript-toolkit
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

## Formatting with gdformat

Coming mid February 2020.

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
