# Changelog

## [master]

### Changed
 - Fixed linter problem reports when global scope is used
 - Fixed formatting of certain `@warning_ignore` annotations

## [4.3.3] 2024-11-02

### Changed
 - Fixed false-positive `expression-not-assigned` linter check on lambdas
 - Fixed erroneous DedentError raised in case of inline lambas

## [4.3.2] 2024-10-20

### Added
 - Added support for multi-statement lambdas (#191)
 - Added support for typed dictionaries (#322)

### Changed
 - Removed `private-method-call` linter check due to false positives when calling `super._foo()`
 - Fixed support for `get_node` syntax to accommodate for `$/(...)`
 - Fixed `gd2py` and `gdradon` to support latest GDScript
 - Changed formatting of some uni-statement lambdas
 - Changed formatting of multi-statement, inline lambdas
 - Changed formatting of dot-chains containing a lambda(s)
 - Changed linter check `class-definitions-order` in a way that static class variables are recommended to be placed just after constants

## [4.3.1] 2024-08-24

### Added
 - Added support for `is not` type test

## [4.3.0] 2024-08-18

### Added
 - Added `gdformatrc` configuration file to `gdformat`
 - Added support for Allman-style enum definitions to parser
 - Added support for string-based unique node names
 - Added support for properties in `gd2py`
 - Added support for `get():` property syntax
 - Added support for multiline arrays and dictionaries in `match` statement branches
 - Added support for guarded `match` branches

### Changed
 - Fixed support for `breakpoint` statement in formatter
 - Fixed nested unique name (`%`)

## [4.2.2] 2023-12-11

### Changed
 - Fixed support for r-strings

## [4.2.1] 2023-12-10

### Added
 - Added support for multiline patterns within `match` statement branches
 - Added support for r-strings

## [4.2.0] 2023-11-30

### Added
 - Added support for `breakpoint` statement
 - Added support for function-level annotations
 - Added support for typed `for` loop iterator (#241)
 - Added the `--use-spaces=<int>` option to `gdformat` so that space-based indentations can be used instead of tab-based ones

### Changed
 - Fixed `max-public-methods` linter check disabling (#222)
 - Default regex for names of constants now allows underscore as a prefix to denote private contants (#223)
 - Fixed parsing of files without newline at the end of file ending with comment (#237)
 - Fixed linter support for docstrings (#233)
 - Fixed linter support for trailing comma in function's args list (#206)
 - Fixed linter support for static variables and classnames bundled with `extends` (#242)
 - Enforced function statement annotations to be formatted to separate lines (#252)

## [4.1.0] 2023-07-06

### Added
 - Added support for `not in` operator
 - Added support for `static` class variables

### Changed
 - Improved exceptions formatting

## [4.0.1] 2023-04-22

### Added
 - Added support for user-defined types in type hints
 - Added support for annotations with empty argument list (e.g. `@onready()`)
 - Added support for power operator `**`

### Changed
 - Fixed `max-returns` check's message
 - Fixed formatting of `static` functions

## [4.0.0] 2023-03-01

### Added
 - Added new GDScript `2.0` constructs to the core testcases
 - Added support for `await`
 - Added support for typed arrays
 - Added support for annotations
 - Added support for unique node names
 - Added support for property etters
 - Added support for inline-lambdas
 - Added support for func-level constants
 - Added support for typed signal arguments

### Changed
 - Removed support for legacy (Godot `3.x`) GDScript from core testcases
 - Updated `lark` dependency to the latest release - `1.1.5`
 - Improved `subscr_expr`/`getattr`/`getattr_call` chains formatting

## [3.4.0] 2022-04-21

### Added
 - Added `no-elif-return` linter check
 - Added `no-else-return` linter check
 - Added `gd2py` (GDScript-to-python) converter tool
 - Added `gdradon` code metrics tool

### Changed
 - Workarounded a lark error impacting pretty print in frontends
 - Fixed lack of trailing comma handler in some corner cases
 - Fixed lack of support for plus prefixed expressions
 - Fixed lack of support for `Vector2/3()` in `match` patterns
 - Fixed formatter's corner case in `func()`

## [3.3.1] 2021-09-15

### Added
 - Added support for `export onready var` statement on `class` level
 - Added support for `mastersync` and `puppetsync` functions
 - Added support for standalone comments in expressions (except for few corner-cases)
 - Added `--diff` option to `gdformat` which acts the same as `--check`, but with additional difference printing
 - Added support for single line pattern formatting (forced for now)
 - Added `--fast` option to `gdformat` to skip safety checks (thus being faster)

### Changed
 - Fixed exception handling in `gdparse`, `gdlint`, and `gdformat`
 - Fixed adding newlines around non-standard functions like `static func`, `master func` etc.
 - Fixed if-stmt-related corner case where formatting shred a colon
 - Changed formatter to keep going despite failures

## [3.3.0] 2021-08-31

### Added
 - Added support for `pass` statement on `class` level
 - Added a possibility to disable linter checks in range from e.g. `# gdlint: disable=function-name` to `# gdlint: enable=function-name`
 - Added support for `puppet var`
 - Added string formatting according to `GDScript style guide` (`'x'` -> `"x"`, `'"'` -> `'"'`. `"'"` -> `"'"`, `'"\''` -> `"\"'"`)
 - Added linter option `tab-characters` that allows treating tabs as multiple characters while calculating line length

### Changed
 - Fixed comment persistence check
 - Improved comments handling
 - Improved utf-8 support
 - Fixed type cast (e.g. `1 as String`) to always be in one line (this is forced by Godot's bug)

## [3.2.8] 2020-09-15

### Added
 - Added support for legacy (godot `3.1`) parenthesesless `assert` (e.g. `assert 1 == 1`)
 - Added support for recursive file finding in `gdlint` (e.g. `gdlint dir1/ dir2/`)
 - Added pre-commit hooks which can consumed by `pre-commit` project
 - Added a possibility to ignore linter checks inplace (e.g. `# gdlint: ignore=function-name` inline or in the line before)
 - Added support for underscored numeric literals such as `1_000_000`, `1_000.000`, and `0xff_99_00`

### Changed
 - Introduced WA for Godot's `preload` bug
 - Improved formatter to remove trailing whitespaces also from comments
 - Added missing `class_name (...) extends (...)` statement support in grammar and formatter
 - Fixed false positive `TreeInvariantViolation` for `neg_expr`
 - `var x = load('some.tres')` is allowed since it may be custom resource instance loading

## [3.2.7] 2020-05-08

### Changed
 - Added missing expression operators (`^=`, `>>=`, and `<<=`)

## [3.2.6] 2020-04-05

### Changed
 - Improved comment parsing time by a tiny chunk
 - Improved formatting time due to loosen grammar removal
 - Improved formatting time due to grammar caching
 - Improved formatting time due to parse tree reuse in safety checks
 - Fixed bug in grammar causing func suite to consume statements from outer scope
 - Enum doesn't add trailing comma unless it was in place from the very beginning
 - Level-0 standalone comments are not indented anymore

## [3.2.5] 2020-02-09

### Changed
 - Formatting strings with hash inside
 - Fixed getattr call formatting bug
 - Fixed 'extends' formatting bug

## [3.2.4] 2020-02-06

### Changed
 - Fixed parent block comments in if-elif-else
 - Fixed parentheses handling in formatter
 - Improved fromatter's dedent lookup
 - Fixed 'extends' bug in grammar
 - Fixed grammar - types allow dots now

## [3.2.3] 2020-02-04

### Changed
 - Type inference in grammar
 - Improved linter exec user experience
 - Fixed linter hanging on config file not present

## [3.2.2] 2020-02-03

### Changed
 - Missing grammar file added

## [3.2.1] 2020-02-02

### Changed
 - Package metadata

## [3.2.0] 2020-02-02

### Added
 - Grammar
 - Parser (`gdparse`)
 - Linter (`gdlint`) with some basic checks
 - Formatter (`gdformat`) which should work for most of real-life scenarios
