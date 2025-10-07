---@class PylofMarksSecondOrder
---@field open string|string[] Opening of an oscillating mark.
---@field oscillator { turn: string|string[], re-entry: string|string[] } Memory function.
---@field counter { state-switch: string|string[], re-entry: string|string[] } Counter function.

---@class PylofMarks
---@field first-order { open: string|string[], close: string|string[] }
---@field second-order PylofMarksSecondOrder

---@class PylofConnectives
---@field command table
---@field symbol table

---@class PylofHelper
---@field ref-label string|string[] Reference label.
---@field escape { symbol: string|string[], block: string|string[] } Escaped elements.
---@field special-block string|string[] Externally managed block if a `parse_special(height, content)` function is provided. Otherwise treated like an escape block.
---@field sigil string|string[] Placeholder and in doubling command prefix.

---@class PylofSyntax
---@field helper PylofHelper
---@field connective table
---@field mark PylofMarks

local def = {}

def.syntax = {
	helper = {
		["ref-label"] = { ".", ",", ";" },
		escape = {
			next = "\\",
			block = "/",
			["special-block"] = "//",
		},
		sigil = { ":", "-" },
	},
	connective = {
		command = {
			definition = "defined_as",
			negation = "not",
			identity = "is_equal",
			implication = "implies",
			["inverted-implication"] = "is",
			equivalence = "iff",
			conjunction = "and",
			disjunction = "or",
			["exclusive-disjunction"] = "or_instead"
		},
		symbol = {
			definition = ":=",
			negation = { "!", "~" },
			identity = { "=" },
			implication = { "->", "=>" },
			["inverted-implication"] = { "<=", "<-" },
			equivalence = { "<=>", "<->" },
			conjunction = "&",
			disjunction = "/",
			["exclusive-disjunction"] = "//"
		},
	},
	mark = {
		["first-order"] = {
			open = "(",
			close= ")",
		},
		["second-order"] = {
			["re-entry"] = {
				["from-left"] = ">",
				["from-right"] = "<"
			},
			open = "[",
			turn = "]",
			switch = "|",
			["switch-mark"] = "{",
			["switch-unmark"] = "}",
		}
	},
}

return def
