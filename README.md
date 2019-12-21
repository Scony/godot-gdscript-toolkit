# GDScript Toolkit
[![](https://travis-ci.org/Scony/godot-gdscript-toolkit.svg?branch=master)](https://travis-ci.org/Scony/godot-gdscript-toolkit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project aims to create an E2E set of tools for daily work with `GDScript`. The ultimate goal is to provide tools such as:

* parser - producing a parse tree for debug/educational purposes
* compiler - producing an easy to use intermediate representation (IR)
* linter - performing a static analysis according to some predefined configuration
* formatter - formatting the code according to some predefined rules

## Current status

The grammar and parser are done (may have minor issues). The linter is under WIP, although it already has some useful checks.

## Installation

To install this project you will need `python3` and `pip`. The command is as follows:

```
$ pip install git+https://github.com/Scony/godot-gdscript-toolkit
```

## Linter - gdlint

To run a linter you need to perform installation first. Once done, you can run e.g.:

```
$ gdlint misc/MarkovianPCG.gd
misc/MarkovianPCG.gd:96: Error: Function argument name "aOrigin" is not valid (function-argument-name)
misc/MarkovianPCG.gd:96: Error: Function argument name "aPos" is not valid (function-argument-name)
misc/MarkovianPCG.gd:96: Error: Function argument name "aType" is not valid (function-argument-name)
misc/MarkovianPCG.gd:96: Error: Function argument name "aConnections" is not valid (function-argument-name)
misc/MarkovianPCG.gd:222: Error: Function argument name "aConnections" is not valid (function-argument-name)
```

In order to tweak the default check settings (regexes, thresholds etc.) you can easily dump default config to a file:

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

## Parser - gdparse

To run a parser you need to perform installation first. Once done, you can run e.g.:

```
$ gdparse tests/valid-gd-scripts/recursive_tool.gd -p
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

If parser succeeded, it will return the exit code `0`.

## Running tests

To run tests you will need `tox`. To invoke entire test suite run:

```
$ tox
```

To run only selected test cases run e.g.
```
tox -e py3 -- -k lint
```
