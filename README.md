# GDScript Toolkit
[![](https://github.com/Scony/godot-gdscript-toolkit/workflows/Tests/badge.svg)](https://github.com/Scony/godot-gdscript-toolkit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Buy me a coffe](https://img.shields.io/badge/Buy%20me%20a%20coffe-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/pawel_lampe)

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

## Using gdtookit in pre-commit

To add gdtookit as a pre-commit hook check the latest GitHub version (eg `4.2.2`) and add the followingto your `pre-commit-config.yaml` with the latest version.

```Yaml
repos:
  # GDScript Toolkit
  - repo: https://github.com/Scony/godot-gdscript-toolkit
    rev: 4.2.2
    hooks:
      - id: gdlint
        name: gdlint
        description: "gdlint - linter for GDScript"
        entry: gdlint
        language: python
        language_version: python3
        require_serial: true
        types: [gdscript]
      - id: gdformat
        name: gdformat
        description: "gdformat - formatter for GDScript"
        entry: gdformat
        language: python
        language_version: python3
        require_serial: true
        types: [gdscript]
```

## Linter plugins

gdlint supports external plugins for custom lint rules. A plugin is a Python module that exposes a `lint(parse_tree, config)` function and returns a list of `Problem` objects.

### Example: creating a custom rule

1. Create a plugin file `no_print_checks.py` in your project root:

```python
from types import MappingProxyType
from typing import List

from lark import Tree, Token
from gdtoolkit.linter.problem import Problem
from gdtoolkit.common.utils import get_line, get_column


def lint(parse_tree: Tree, config: MappingProxyType) -> List[Problem]:
    if "no-print-statement" in config.get("disable", []):
        return []
    problems = []
    for call_node in parse_tree.find_data("standalone_call"):
        for child in call_node.children:
            if isinstance(child, Token) and child.value == "print":
                problems.append(Problem(
                    name="no-print-statement",
                    description="Avoid using print() in production code",
                    line=get_line(child),
                    column=get_column(child),
                ))
            break
    return problems
```

The `Problem` dataclass has four fields: `name` (rule identifier — this is what you use to disable the rule), `description` (human-readable message), `line`, and `column`.

2. Add the plugin to your `gdlintrc` by module name (filename without `.py`). The `plugins` key sits alongside the same settings you already use:

```yaml
# gdlintrc
class-name: '([A-Z][a-z0-9]*)+'
constant-name: '[A-Z][A-Z0-9]*(_[A-Z0-9]+)*'
max-line-length: 100
disable: []
plugins:
  - no_print_checks
```

3. Run `gdlint` — the plugin rule works exactly like built-in rules:

```
$ gdlint my_script.gd
my_script.gd:5: Error: Avoid using print() in production code (no-print-statement)
```

### How plugins are loaded

Plugin names can be either **module names** or **relative paths**:

```yaml
plugins:
  # module name — loaded via importlib, must be on sys.path
  - no_print_checks
  # relative path — loaded from file relative to cwd (no .py extension)
  - ci/gdlint/no_print_checks
```

When plugins are configured, the current working directory is automatically added to `sys.path`, so local `.py` files are found by module name. For plugins in subdirectories, use the path form — forward slashes work on all platforms.

Missing or failing plugins are logged as warnings and skipped — they won't crash the linter.

### Distributing plugins as packages

For sharing plugins across projects, structure your plugin as a pip-installable Python package with a `setup.py` or `pyproject.toml`:

```
my-gdlint-plugin/
  my_gdlint_plugin/
    __init__.py      # must contain lint(parse_tree, config)
    some_check.py
  setup.py
```

Then install and reference the module name in `gdlintrc`:

```
pip install my-gdlint-plugin
```

```yaml
plugins:
  - my_gdlint_plugin
```

### Using plugins with pre-commit

pre-commit runs hooks in isolated virtualenvs, so neither local `.py` files nor globally installed packages are available. Use [`additional_dependencies`](https://pre-commit.com/#config-additional_dependencies) to install plugin packages into the hook's environment.

`additional_dependencies` accepts anything pip can install — a PyPI package, a git URL, or a local path:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Scony/godot-gdscript-toolkit
    rev: 4.2.2
    hooks:
      - id: gdlint
        additional_dependencies:
          # from PyPI:
          - my-gdlint-plugin==1.0.0
          # from a git repo:
          - git+https://github.com/your-org/my-gdlint-plugin.git@main
          # from a local directory (editable install):
          - -e ./linter/my-gdlint-plugin
```

## Development [(more)](https://github.com/Scony/godot-gdscript-toolkit/wiki/5.-Development)

Everyone is free to fix bugs or introduce new features. For that, however, please refer to existing issue or create one before starting implementation.
