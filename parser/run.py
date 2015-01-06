from GrammarParser import *
import json
import argparse
import os.path


def printer(level, msg):
    print((" "*level) + msg)


def run():
    # Command-line stuffs
    parser = argparse.ArgumentParser(description="GrammarParser demo program.", usage="%(prog)s [options] source [grammar]")
    parser.add_argument("-v", "--validate", dest="validate", action="store_true", default=False, help="validate all rule in the grammar")
    parser.add_argument("-p", "--print", dest="print_call", action="store_true", default=False, help="print rule calls")
    parser.add_argument("-m", "--multiple", dest="multiple", action="store_true", default=False, help="enable multiple selector")
    parser.add_argument("-g", "--grammar", dest="grammar", nargs="?", default="example.json", type=str, help="grammar file to use (default is example.json)")
    parser.add_argument("-r", "--regex", dest="regex", nargs="?", type=str, help="RegEx selector")
    parser.add_argument("-s", "--selector", dest="selector", nargs="?", type=str, help="node selectors")
    parser.add_argument("source", nargs="?", type=str, help="source file to parse with grammar")
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
        if options.selector is not None:
            nodes = parser.find_by_selectors(options.selector)
        elif options.regex is not None:
            nodes = parser.find_by_regex(options.regex)
        else:
            nodes = parser.find_all()
        index = 1
        for node in nodes:
            print("#{0}, {1}-{2} => {3}".format(index, node["begin"], node["end"], node["name"]))
            print("   => " + node["value"])
            index += 1
        print("Total: " + str(len(nodes)) + " tokens")
        while True:
            selectors = raw_input("Selectors> ")
            if selectors == "":
                break
            nodes = parser.find_by_selectors(selectors, nodes)
            # Print it out
            index = 1
            for node in nodes:
                print("#{0}, {1}-{2} => {3}".format(index, node["begin"], node["end"], node["name"]))
                print("   => " + node["value"])
                index += 1
            print("Total: " + str(len(nodes)) + " tokens")
            if not options.multiple:
                break
    # Parsing position compare to data size
    print("Ending: " + str(parse_output["end"]) + "/" + str(len(source_data)))
    # Parsing time (filtering is not included)
    print("Time: {elapse_time:.2f}s".format(elapse_time=parser.get_elapse_time()))

if __name__ == "__main__":
    run()
