from GrammarParser import *
import sys, json, argparse, os.path

def printer(level, msg):
    print((" "*level) + msg)

def run():
    # Command-line stuffs
    parser = argparse.ArgumentParser(description="GrammarParser demo program.", usage="%(prog)s [options] source [grammar]")
    parser.add_argument("-v", "--validate", dest="validate", action="store_true", default=False, help="validate all rule in the grammar")
    parser.add_argument("-p", "--print", dest="print_call", action="store_true", default=False, help="print rule calls")
    parser.add_argument("source", nargs="?", type=str, help="source file to parse with grammar")
    parser.add_argument("grammar", nargs="?", default="example.json", type=str, help="grammar file to use (default is example.json)")
    options = parser.parse_args()

    # Show help if nothing is provided
    if options.source is None:
        parser.print_help()
        return

    # Confirm the files
    if not os.path.exists(options.source):
        print("Error: Source file is not found")
        return
    elif not os.path.exists(options.grammar):
        print("Error: Grammar file is not found")
        return
    print("Grammar: " + options.grammar)
    print("Source: " + options.source)
    source_data = open(options.source, "r").read()
    grammar_data = open(options.grammar, "r").read()

    # Remove comment since JSON does not supported it
    # This RegEx only remove line comment (//comment)
    grammar = json.loads(re.sub("(?<=[\\r\\n])\\s*//[^\\r\\n]*(?=[\\r\\n])", "", grammar_data))

    # Create a new instance of GrammarParser
    if options.print_call:
        # With printer
        parser = GrammarParser(grammar, printer)
    else:
        # Without printer
        parser = GrammarParser(grammar)

    # Validate grammar?
    if options.validate:
        validate_output = parser.validate_grammar()

        unused_rules = validate_output["unused_rules"]
        # Show all unused rules
        if len(unused_rules) > 0:
            print("Unused Grammar Rules")
            index = 1
            for unused in unused_rules:
                print(str(index) + ". " + unused)
                index += 1

        # Show all unexists rules
        unexists_rules = validate_output["unexists_rules"]
        if len(unexists_rules) > 0:
            print("Unexists Grammar Rules")
            index = 1
            for unexists in unexists_rules:
                print(str(index) + ". " + unexists)
                index += 1

        raw_input("Press enter/return to continue...")

    # Parse a source data
    parse_output = parser.parse_grammar(source_data)
    # Parsing success?
    if parse_output["success"]:
        ##################################################
        # Uncomment line below to narrow down the output #
        ##################################################
        ## Show method name by searching from node name ##
        # nodes = parser.find_by_selector("@MethodName")

        ## Show all nodes that have Comment as their parent ##
        # nodes = parser.find_by_selectors("Comment>")

        ## Show Comment nodes and also their childs ##
        # nodes = parser.find_by_selectors("Comment|Comment>")

        ## Show only block that inside method body using RegEx ##
        # nodes = parser.find_by_regex(".*MethodBody>Block$")

        ## Show all nodes contains specified region ##
        # nodes = parser.find_by_region([120, 145])

        ## Show all nodes inside specified region ##
        # nodes = parser.find_inside_region([120, 145])

        ## Show all tokens ##
        nodes = parser.find_all()
        #######################
        # Selection filtering #
        #######################
        ## Show all method declarations within selected nodes ##
        nodes = parser.find_by_selector("@MethodDeclaration", nodes)

        # Print it out
        index = 1
        for node in nodes:
            print("#{0}, {1}-{2} => {3}".format(index, node["begin"], node["end"], node["name"]))
            print("   => " + node["value"])
            index += 1
        print("Total: " + str(len(nodes)) + " tokens")
    # Parsing position compare to data size
    print("Ending: " + str(parse_output["end"]) + "/" + str(len(source_data)))
    # Parsing time (filtering is not included)
    print("Time: {elapse_time:.2f}s".format(elapse_time=parser.get_elapse_time()))

if __name__ == "__main__":
    run()
