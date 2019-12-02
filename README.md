# GDScript Toolkit
[![](https://travis-ci.org/Scony/godot-gdscript-toolkit.svg?branch=master)](https://travis-ci.org/Scony/godot-gdscript-toolkit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project aims to create an E2E set of tools for daily work with `GDScript`. The ultimate goal is to provide tools such as:

* parser - producing a parse tree
* compiler - producing an easy to use intermediate representation (IR)
* linter - performing a static analysis according to some predefined configuration
* formatter - formatting the code according to some predefined rules

## Current status

The grammar and parser are mostly done, but still under some WIP.

## Installation

To install this project you will need `python3` and `pip`. The command is as follows:

```
$ pip install git+https://github.com/Scony/godot-gdscript-toolkit
```

## Parser

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

To run tests you will need `python` and `tox`. To invoke test suite run:

```
$ tox
```
