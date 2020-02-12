# GDScript Formatter

This runs Scony's python-based GDScript formatter.

## Features

Formats GDScript code using VSCode's built-in formatters. Supports format-on-save.

Usage: `ctrl`+`shift`+`P` to open the command palette. `Format Document` on a GDScript file.

![Formatted output](https://github.com/Scony/godot-gdscript-toolkit/blob/vscode-plugin/editor-plugins/vscode/assets/banner.png)

## Requirements

- `Python3` and `pip` should both be installed.
- The `GDToolkit` module should be installed via pip, though if it is missing you will be prompted to install it.

## Extension Settings

- `gdscript_formatter.line_size`: The maximum size a given line can be before it is wrapped.

## Known Issues

None yet

## Release Notes

### 1.0.0

Initial release of the VSCode extension of GDScript Formatter.
