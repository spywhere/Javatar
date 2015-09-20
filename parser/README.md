## Grammar Parser

A Python lexerless recursive descent grammar parser

### Usage
Place files from this repository anywhere in your project and import by using `from GrammarParser import *` or `from GrammarParser import GrammarParser` or similar.

For better understanding, check out an example included within this repository.

**IMPORTANT: Grammar Parser has no version. Please check this repository for any update.**

### Parsing
Before start parsing, you will need to create a new instance of GrammarParser...

```py
parser = GrammarParser(grammar)
```

If you want to print the rule calls, you need to specified a callback (in this case, printer function) in constructor...

```py
parser = GrammarParser(grammar, printer)
```
	
Printer function will receive 2 arguments from GrammarParser.

 - `level`
   - Level is recursion level of current rule. This is used to offset the screen to act like nested function.
 - `message`
   - Message is an information from parser. From starting rule to end.

For grammar, please refer to Language Grammar section below.

After you instantiate a new GrammarParser, you can parse document by...

```py
parse_output = parser.parse_grammar(source_data)
```

Source data is just data you want to parse with grammar. The output is a Python dictionary contains...

 - `success`
   - Boolean indicate that parser successfully parsed the document or not.
 - `begin`
   - An integer indicate a starting position
 - `end`
   - An integer indicate an ending position (compare this value to the size of data can indicate 100% successful parsing)
 
#### Difference between `success` and `end`
Let's say you have a Python document and we will parse it using Java grammar. The compilation unit of Java is simply an optional of package declaration, multiple (equivalent to star in Regular Expression) of import declarations and multiple of type declarations.

When you parse the document, parser will return `success` as `True` and `end` as `0` since Python document has 0 package declaration (it is optional so it can be omitted), 0 import declaration (it is multiple so it can be omitted) and 0 type declaration (it is multiple again so it can be omitted too).

That is not correct, right?

So, if you want to ensure 100% successful parsing, you may want to use both `success` and `end` to check if `success` is `True` and `end` is at the last position of document.

### Selectors
When parsing is finished, you can select a portion of nodes (or tokens) to use. There are many ways you can select a specific one...

 - Find by selector
	```py
	nodes = parser.find_by_selector(selector)
	```

	Selector is simply a string which is part of call tree.
	As default, the selector will select any nodes that its call tree *starts with* the selector. If you want the selector to select any nodes that its call tree *contains* the selector, just add `>` at start of the selector.
	
	You can let it search using node name by specified `@` at start of the selector. And if you want to show its childs (if any) you might add `>` at the end of the selector.


	To summarize, here is the selector format...
	
		[@][>]selector[>]
	
	@ = Search by node name  
	\> (At start) = Find anywhere that contains selector  
	\> (At the end) = Find only its childs

	[ ] indicate that it is an optional option.
	
	Selector also support filtering, by adding `[ChildSelector=Value]` (include braces) to the end of the selector (also after the `>`, if any), will select the only node which qualify for the filter selector.
	
	Filter's selector format is as follows...
	
		[>]selector
	
	\> (At start) = Find anywhere that contains selector
	
 - Find by selector(s)

	```py
 	nodes = parser.find_by_selectors(selectors)
 	```
 	
 	This is works same as find_by_selector but, in this one, you can specified multiple selectors at once. Just separate each selector using `|` and any matched nodes will be selected.
 	
 	The format is just...
 	
 		[@][>]selector[>]|[@][>]selector[>]|...
 	
 	**Note! Spaces are also count as selector name.**
 - Find by RegEx

	```py 
 	nodes = parser.find_by_regex(regex)
 	```
 	
 	This is one of the flexible option to select nodes. RegEx will be matched with call tree as default. Add `@` will switch to node name instead. But in this time, find all and childs flags cannot be set (`>` at start and end of selector) since RegEx can check all of that by specified a RegEx pattern.
 - Find by region

	```py 
 	nodes = parser.find_by_region([start, end])
	```
 	
 	This is use when you want to select all nodes that *covered* specified region.
 
 - Find inside region

	```py
 	nodes = parser.find_inside_region([start, end])
 	```
 	
 	This is used similar to find by region. But this one will find all nodes that *inside* specified region instead.

 - Find all

	```py
	nodes = parser.find_all()
	```
 		
 	This is used when you want to select all nodes.

Output of selector is a nodes list. Nodes list can be find again by adding it at the end of any function above (See example for, well, example). Each node is a Python dictionary contains...

 - `begin`
   - The starting position of node
 - `end`
   - The ending position of node
 - `value`
   - The substring from document that represent this node
 - `parent`
   - The rule calls (consists of `NodeName>NodeName>NodeName>...`)
 - `name`
   - Node name

### Language Grammar
Language grammar is used to parse a document. This grammar must not contains Leftmost-Recursion since this might cause too deep recursion problem.

A language grammar is a Python dictionary which contains 3 root key/value pairs:

 - `separator`
   - This will be used as separator between each token. You can ignore this separator in each rule by specified `before_separator` or `after_separator` key in that rule (more details in Grammar Rule).
 - `compilation_unit`
   - This is a starting symbol of your grammar. Parser will look into this key at first.
 - `repository`
   - This can be used as a rules repository (or rules bank). You can access this repository only by specified `include` key in the rule (more details in Grammar Rule).

Each key is an optional grammar rule. You may want to specified some of them or all of them.

### Grammar Rule
Grammar rule is smallest part of grammar. It is used to match and redirect to another rule by using a key/value pair...
	
 - `name` - String
   - This is used to named a node or a token which you can select by selector (with `@`).
 - `exclude` - Grammar Rule
   - This is used to pre-parse the rule. If current token matched with this rule, that token will considered an invalid and will be parsed by next rule (useful when you need to reject identifier from using keyword).
 - `match` - String
   - This is the only part that is terminal symbol. Match is simply a RegEx pattern to match specific portion of document.
 - `before_separator` - Boolean
   - This is used to stop separator from parsing before match (useful in some cases).
 - `after_separator` - Boolean
   - This is used to stop separator from parsing after match (useful in some cases).
 - `parse` - List
   - This is a list of Grammar Rules. Parse will considered current token valid when *all* rules are valid.
 - `parse_any` - List
   - This is a list of Grammar Rules. Parse any will considered current token valid when *one of* rules is valid.
 - `include` - String
   - This is used to include a rule from repository to itself. Very useful when you want to include a rule from another rule.
 - `optional` - Boolean
   - This is used to specified current rule as optional. That is mean if this rule is invalid, it will still valid. Works same as `?` in RegEx.
 - `multiple` - Boolean
   - This is used to specified current rule as multiple occurrance. That is mean this rule will matched multiple times as possible. Works same as `*` in RegEx.

`match`, `parse`, `parse_any` and `include` cannot be used at the same time (only one per rule). This prevent a problem may cause in later version when reorder a priority.
	
### Validate Grammar
When you finish create a new language grammar, you might want to check if any of rules are not used or unexists. You can validate your grammar by...

```py
validate_output = parser.validate_grammar()
```

The output from validation is a Python dictionary contains...

 - `unused_rules`
   - Just a list of unused rules
 - `unexists_rules`
   - Just a list of unexists rules

### License

	::GrammarParser::
	
	The MIT License (MIT)
	
	Copyright (c) 2014 Sirisak Lueangsaksri
	
	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:
	
	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.
	
	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.
