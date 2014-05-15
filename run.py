from GrammarParser import *
import sys, json

def printer(level, msg):
	print((" "*level) + msg)

def run(args):
	# Command-line stuffs
	validate = False
	print_calls = False
	source_file = None
	grammar_file = None
	skip = True
	for arg in args:
		# Skip first argument
		if skip:
			skip = False
			continue
		if arg == "-v":
			validate = True
		elif arg == "-p":
			print_calls = True
		else:
			if source_file is None:
				source_file = arg
			elif grammar_file is None:
				grammar_file = arg
	if source_file is None:
		print("Usage: " + args[0] + " [options] <source file> [grammar file]")
		print("    Default grammar will be example.json file")
		print("Options:")
		print("  -v")
		print("    Validate grammar")
		print("  -p")
		print("    Print rule calls")
		return
	if grammar_file is None:
		grammar_file = "example.json"
	print("Grammar: " + grammar_file)
	print("Source: " + source_file)
	source_data = open(source_file, "r").read()
	grammar_data = open(grammar_file, "r").read()

	# Remove comment since JSON does not supported it
	# This RegEx only remove line comment (//comment)
	grammar = json.loads(re.sub("(?<=[\\r\\n])\\s*//[^\\r\\n]*(?=[\\r\\n])", "", grammar_data))

	# Create a new instance of GrammarParser
	if print_calls:
		# With printer
		parser = GrammarParser(grammar, printer)
	else:
		# Without printer
		parser = GrammarParser(grammar)

	# Validate grammar?
	if validate:
		validate_output = parser.validate_grammar()

		unused_rules = validate_output["unused_rules"]
		if len(unused_rules) > 0:
			print("Unused Grammar Rules")
			index = 1
			for unused in unused_rules:
				print(str(index) + ". " + unused)
				index += 1

		unexists_rules = validate_output["unexists_rules"]
		if len(unexists_rules) > 0:
			print("Unexists Grammar Rules")
			index = 1
			for unexists in unexists_rules:
				print(str(index) + ". " + unexists)
				index += 1

		input("Press enter/return to continue...")

	# Parse a source data
	parse_output = parser.parse_grammar(source_data)
	# Parsing success?
	if parse_output["success"]:
		###################################
		# Show method name by searching from node name
		# nodes = parser.find_by_selector("@MethodName")

		# Show all nodes that have Comment as their parent
		# nodes = parser.find_by_selectors("Comment>")

		# Show Comment nodes and also their childs
		# nodes = parser.find_by_selectors("Comment|Comment>")

		# Show only block that inside method body using RegEx
		# nodes = parser.find_by_regex(".*MethodBody>Block$")

		# Show all nodes contains specified region
		# nodes = parser.find_by_region([120, 145])

		# Show all nodes inside specified region
		# nodes = parser.find_inside_region([120, 145])

		# Show all tokens
		nodes = parser.find_all()
		###################################
		# Show all method declarations within selected nodes
		nodes = parser.find_by_selector("@MethodDeclaration", nodes)
		###################################
		index = 1
		for node in nodes:
			print("#{0}, {1}-{2} => {3}".format(index, node["begin"], node["end"], node["name"]))
			print("   => " + node["value"])
			index += 1
		print("Total: " + str(len(nodes)) + " tokens")
	# Parsing position compare to data size
	print("Ending: " + str(parse_output["end"]) + "/" + str(len(source_data)))
	# Parsing time (searching is not included)
	print("Time: {elapse_time:.2f}s".format(elapse_time=parser.get_elapse_time()))

if __name__ == "__main__":
	run(sys.argv)