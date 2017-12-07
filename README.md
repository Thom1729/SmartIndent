# SmartIndent
Syntax-based indentation for Sublime Text

**This package is a proof of concept that may be unsuited to production use. Use with caution.**

Sublime's built-in indentation system (inherited from TextMate) uses regular expressions to indent and unindent lines. Smart Indent is a more sophisticated approach that uses scope information supplied by the current syntax definition.

Smart Indent should work well for syntaxes that:

- Supply plenty of meta scopes.
- Mark closing punctuation with `end`.
- Do not have significant whitespace.

In some languages, such as Python, this approach is likely to work *extremely poorly*.

## Usage

Clone this package using git. I will probably submit it to Package Control eventually.

The Smart Indent command is bound by default to <kbd>ctrl</kbd>+<kbd>F9</kbd>. Running this command will reindent the current view.