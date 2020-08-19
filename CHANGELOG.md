# Changelog

## master

### Added
 - Added support for legacy (godot 3.1) parenthesesless `assert` (e.g. `assert 1 == 1`)
 - Added support for recursive file finding in `gdlint` (e.g. `gdlint dir1/ dir2/`)
 - Added pre-commit hooks which can consumed by `pre-commit` project

### Fixed
 - Introduced WA for Godot's `preload` bug
 - Improved formatter to remove trailing whitespaces also from comments
 - Added missing `class_name (...) extends (...)` statement support in grammar and formatter
 - Fixed false positive `TreeInvariantViolation` for `neg_expr`

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
