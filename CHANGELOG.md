# Changelog

## [master]

### Added
 - Added support for user-defined types in type hints
 - Added support for annotations with empty argument list (e.g. `@onready()`)
 - Added support for power operator `**`

### Fixed
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

### Fixed
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

### Fixed
 - Fixed exception handling in `gdparse`, `gdlint`, and `gdformat`
 - Fixed adding newlines around non-standard functions like `static func`, `master func` etc.
 - Fixed if-stmt-related corner case where formatting shred a colon

### Changed
 - Changed formatter to keep going despite failures

## [3.3.0] 2021-08-31

### Added
 - Added support for `pass` statement on `class` level
 - Added a possibility to disable linter checks in range from e.g. `# gdlint: disable=function-name` to `# gdlint: enable=function-name`
 - Added support for `puppet var`
 - Added string formatting according to `GDScript style guide` (`'x'` -> `"x"`, `'"'` -> `'"'`. `"'"` -> `"'"`, `'"\''` -> `"\"'"`)
 - Added linter option `tab-characters` that allows treating tabs as multiple characters while calculating line length

### Fixed
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

### Fixed
 - Introduced WA for Godot's `preload` bug
 - Improved formatter to remove trailing whitespaces also from comments
 - Added missing `class_name (...) extends (...)` statement support in grammar and formatter
 - Fixed false positive `TreeInvariantViolation` for `neg_expr`

### Changed
 - `var x = load('some.tres')` is allowed since it may be custom resource instance loading

## [3.2.7] 2020-05-08

### Fixed
 - Added missing expression operators (`^=`, `>>=`, and `<<=`)

## [3.2.6] 2020-04-05

### Fixed
 - Improved comment parsing time by a tiny chunk
 - Improved formatting time due to loosen grammar removal
 - Improved formatting time due to grammar caching
 - Improved formatting time due to parse tree reuse in safety checks
 - Fixed bug in grammar causing func suite to consume statements from outer scope

### Changed
 - Enum doesn't add trailing comma unless it was in place from the very beginning
 - Level-0 standalone comments are not indented anymore

## [3.2.5] 2020-02-09

### Fixed
 - Formatting strings with hash inside
 - Fixed getattr call formatting bug
 - Fixed 'extends' formatting bug

## [3.2.4] 2020-02-06

### Fixed
 - Fixed parent block comments in if-elif-else
 - Fixed parentheses handling in formatter
 - Improved fromatter's dedent lookup
 - Fixed 'extends' bug in grammar
 - Fixed grammar - types allow dots now

## [3.2.3] 2020-02-04

### Fixed
 - Type inference in grammar
 - Improved linter exec user experience
 - Fixed linter hanging on config file not present

## [3.2.2] 2020-02-03

### Fixed
 - Missing grammar file added

## [3.2.1] 2020-02-02

### Fixed
 - Package metadata

## [3.2.0] 2020-02-02

### Added
 - Grammar
 - Parser (`gdparse`)
 - Linter (`gdlint`) with some basic checks
 - Formatter (`gdformat`) which should work for most of real-life scenarios
