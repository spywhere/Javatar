'''
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
'''

import re
from time import clock


class GrammarParser():
    def __init__(self, grammar, printer=None):
        self.grammar = grammar
        self.printer = None
        if printer is not None:
            self.printer = printer
        self.re_cache = {}
        self.regions = []
        self.data = None
        self.unused_rules = []
        self.unexists_rules = []

    def contain_rule(self, rule_name):
        return "repository" in self.grammar and rule_name in self.grammar["repository"]

    def validate_rule_list(self, rules):
        for rule in rules:
            self.validate_rule(rule)

    def validate_rule(self, rule):
        if "exclude" in rule:
            self.validate_rule(rule["exclude"])
        if "parse" in rule:
            self.validate_rule_list(rule["parse"])
        if "parse_any" in rule:
            self.validate_rule_list(rule["parse_any"])
        if "include" in rule:
            if not self.contain_rule(rule["include"]) and rule["include"] not in self.unexists_rules:
                self.unexists_rules.append(rule["include"])
            else:
                if rule["include"] in self.unused_rules:
                    while rule["include"] in self.unused_rules:
                        self.unused_rules.remove(rule["include"])
                    self.validate_rule(self.grammar["repository"][rule["include"]])

    def validate_grammar(self, first=True):
        if first:
            self.unexists_rules = []
            self.unused_rules = []
            if "repository" in self.grammar:
                for rule_name in self.grammar["repository"]:
                    self.unused_rules.append(rule_name)
        if "separator" in self.grammar:
            self.validate_rule(self.grammar["separator"])
        if "compilation_unit" in self.grammar:
            self.validate_rule(self.grammar["compilation_unit"])
        self.unexists_rules.sort()
        self.unused_rules.sort()
        return {"unused_rules": self.unused_rules, "unexists_rules": self.unexists_rules}

    def parse_grammar(self, data):
        if self.data is None or self.data != data:
            self.data = data
            self.regions = []
        else:
            if self.printer is not None:
                self.printer(0, "Already parse")
            return True
        starttime = clock()
        if "compilation_unit" in self.grammar:
            if self.printer is not None:
                self.printer(0, "== Compilation unit ==")
            begin = 0
            # Pre separator (for beginning correction)
            if ("before_separator" not in self.grammar["compilation_unit"] or self.grammar["compilation_unit"]["before_separator"]):
                separator_output = self.parse_rule(self.grammar["separator"], True, "", 0, 0)
                if separator_output["successive_match"]:
                    begin = separator_output["end"]
                    self.regions += separator_output["regions"]
            parse_output = self.parse_rule(self.grammar["compilation_unit"], False, "", 0, begin)
            if parse_output["successive_match"]:
                self.regions += parse_output["regions"]
            # Post separator (for ending correction)
            if ("after_separator" not in self.grammar["compilation_unit"] or self.grammar["compilation_unit"]["after_separator"]):
                separator_output = self.parse_rule(self.grammar["separator"], True, "", 0, parse_output["end"])
                if separator_output["successive_match"]:
                    parse_output["end"] = separator_output["end"]
                    self.regions += separator_output["regions"]
        self.elapse_time = clock()-starttime
        return {"success": parse_output["successive_match"], "begin": parse_output["begin"], "end": parse_output["end"]}

    def parse_rule_list(self, rules, is_separator, parent, level, begin):
        regions = []
        if self.printer is not None and not is_separator:
            self.printer(level, "== Rule list [" + str(len(rules)) + "] ==")
        index = 0
        root_begin = None
        for rule in rules:
            index += 1
            if self.printer is not None and not is_separator:
                self.printer(level, "> Rule ["+str(index)+"/"+str(len(rules))+"] " + str(begin))
            parse_output = self.parse_rule(rule, is_separator, parent, level+1, begin)
            if parse_output["successive_match"]:
                if root_begin is None:
                    root_begin = parse_output["begin"]
                begin = parse_output["new_begin"]
                regions += parse_output["regions"]
            else:
                if self.printer is not None and not is_separator:
                    self.printer(level, "> Failed")
                break
        if root_begin is None:
            root_begin = begin
        parse_output["begin"] = root_begin
        parse_output["regions"] = regions
        return parse_output

    def parse_rule_list_any(self, rules, is_separator, parent, level, begin):
        if self.printer is not None and not is_separator:
            self.printer(level, "== Rule list once [" + str(len(rules)) + "] ==")
        index = 0
        for rule in rules:
            index += 1
            if self.printer is not None and not is_separator:
                self.printer(level, "> Once ["+str(index)+"/"+str(len(rules))+"] " + str(begin))
            parse_output = self.parse_rule(rule, is_separator, parent, level+1, begin)
            if parse_output["successive_match"]:
                if self.printer is not None and not is_separator:
                    self.printer(level, "> Once Success")
                return parse_output
        if self.printer is not None and not is_separator:
            self.printer(level, "> Once Failed")
        return parse_output

    def parse_rule(self, rule, is_separator, parent, level, begin):
        regions = []
        if self.printer is not None and not is_separator:
            if "name" in rule:
                self.printer(level, "== Rule " + rule["name"] + " [" + str(begin) + "] ==")
            else:
                self.printer(level, "== Rule [" + str(begin) + "] ==")
        rule_output = {"successive_match": False, "match": False, "begin": begin, "new_begin": begin, "end": begin, "regions": []}
        if "name" in rule:
            if parent != "":
                parent += ">"
            parent += rule["name"]
        good = True
        if "exclude" in rule:
            exclude_output = self.parse_rule(rule["exclude"], is_separator, parent, level+1, begin)
            if exclude_output["successive_match"]:
                good = False
        if good:
            if "match" in rule:
                if rule["match"] in self.re_cache:
                    re_pattern = self.re_cache[rule["match"]]
                else:
                    re_pattern = re.compile(rule["match"])
                if not is_separator and "separator" in self.grammar and ("before_separator" not in rule or rule["before_separator"]):
                    if self.printer is not None and not is_separator:
                        self.printer(level, "> Separator Before: " + str(begin))
                    separator_output = self.parse_rule(self.grammar["separator"], True, parent, level+1, begin)
                    if separator_output["successive_match"]:
                        begin = separator_output["new_begin"]
                        regions += separator_output["regions"]
                        if self.printer is not None and not is_separator:
                            self.printer(level, "> Match before sep")
                if self.printer is not None and not is_separator:
                    self.printer(level, "> Matching at [" + str(begin) + "]: " + rule["match"])
                matches = re_pattern.search(self.data[begin:len(self.data)])
                if matches is not None and matches.start() == 0:
                    rule_output["successive_match"] = True
                    rule_output["match"] = True
                    rule_output["begin"] = begin
                    rule_output["end"] = begin+matches.end()
                    rule_output["new_begin"] = rule_output["end"]
                    begin = rule_output["end"]
                    if "name" in rule:
                        regions.append({"begin": rule_output["begin"], "end": rule_output["end"], "value": self.data[rule_output["begin"]:rule_output["end"]], "parent": parent, "name": rule["name"]})
                        if self.printer is not None and not is_separator:
                            self.printer(level, "> Adding " + str(rule_output["begin"]) + ":" + str(rule_output["end"]))
                    else:
                        if self.printer is not None and not is_separator:
                            self.printer(level, "> Skip: " + str(rule_output["end"]))
                if not is_separator and rule_output["successive_match"] and "separator" in self.grammar and ("after_separator" not in rule or rule["after_separator"]):
                    if self.printer is not None and not is_separator:
                        self.printer(level, "> Separator After: " + str(rule_output["end"]))
                    separator_output = self.parse_rule(self.grammar["separator"], True, parent, level+1, begin)
                    if separator_output["successive_match"]:
                        begin = separator_output["new_begin"]
                        regions += separator_output["regions"]
                        if self.printer is not None and not is_separator:
                            self.printer(level, "> Match after sep")
            elif "parse" in rule:
                parse_output = self.parse_rule_list(rule["parse"], is_separator, parent, level+1, begin)
                if parse_output["successive_match"]:
                    if "name" in rule:
                        regions.append({"begin": parse_output["begin"], "end": parse_output["end"], "value": self.data[parse_output["begin"]:parse_output["end"]], "parent": parent, "name": rule["name"]})
                    if parse_output["match"]:
                        rule_output["match"] = parse_output["match"]
                    begin = parse_output["new_begin"]
                    rule_output["new_begin"] = parse_output["new_begin"]
                    rule_output["begin"] = parse_output["begin"]
                    rule_output["end"] = parse_output["end"]
                    rule_output["successive_match"] = parse_output["successive_match"]
                    regions += parse_output["regions"]
            elif "parse_any" in rule:
                parse_output = self.parse_rule_list_any(rule["parse_any"], is_separator, parent, level+1, begin)
                if parse_output["successive_match"]:
                    if "name" in rule:
                        regions.append({"begin": parse_output["begin"], "end": parse_output["end"], "value": self.data[parse_output["begin"]:parse_output["end"]], "parent": parent, "name": rule["name"]})
                    if parse_output["match"]:
                        rule_output["match"] = parse_output["match"]
                    begin = parse_output["new_begin"]
                    rule_output["new_begin"] = parse_output["new_begin"]
                    rule_output["begin"] = parse_output["begin"]
                    rule_output["end"] = parse_output["end"]
                    rule_output["successive_match"] = parse_output["successive_match"]
                    regions += parse_output["regions"]
            elif "include" in rule:
                if "repository" in self.grammar and rule["include"] in self.grammar["repository"]:
                    if self.printer is not None and not is_separator:
                        self.printer(level, "> Include " + rule["include"])
                    parse_output = self.parse_rule(self.grammar["repository"][rule["include"]], is_separator, parent, level+1, begin)
                    if parse_output["successive_match"]:
                        if "name" in rule:
                            regions.append({"begin": parse_output["begin"], "end": parse_output["end"], "value": self.data[parse_output["begin"]:parse_output["end"]], "parent": parent, "name": rule["name"]})
                        if parse_output["match"]:
                            rule_output["match"] = parse_output["match"]
                        begin = parse_output["new_begin"]
                        rule_output["new_begin"] = parse_output["new_begin"]
                        rule_output["begin"] = parse_output["begin"]
                        rule_output["end"] = parse_output["end"]
                        rule_output["successive_match"] = parse_output["successive_match"]
                        regions += parse_output["regions"]
                else:
                    rule_output["successive_match"] = False

            if "multiple" in rule and rule["multiple"] and rule_output["successive_match"]:
                if self.printer is not None and not is_separator:
                    self.printer(level, "Multiple: " + str(begin))
                parse_output = self.parse_rule(rule, is_separator, parent, level+1, begin)
                if parse_output["successive_match"]:
                    if "name" in rule:
                        regions.append({"begin": parse_output["begin"], "end": parse_output["end"], "value": self.data[parse_output["begin"]:parse_output["end"]], "parent": parent, "name": rule["name"]})
                    if parse_output["match"]:
                        rule_output["match"] = parse_output["match"]
                    begin = parse_output["new_begin"]
                    rule_output["end"] = parse_output["end"]
                    rule_output["new_begin"] = parse_output["new_begin"]
                    regions += parse_output["regions"]

        if rule_output["successive_match"]:
            if "name" in rule:
                if self.printer is not None and not is_separator:
                    self.printer(level, "> Matched")
        elif ("optional" in rule and rule["optional"]) or ("multiple" in rule and rule["multiple"]):
            rule_output["successive_match"] = True
            if self.printer is not None and not is_separator:
                self.printer(level, "> Optional")
        if "name" in rule:
            if self.printer is not None and not is_separator:
                self.printer(level, "== EndRule " + rule["name"] + " [" + str(begin) + "] ==")
        else:
            if self.printer is not None and not is_separator:
                self.printer(level, "== EndRule [" + str(begin) + "] ==")
        rule_output["regions"] = regions
        return rule_output

    # Find all (return all)
    def find_all(self):
        return self.regions

    # Find by RegEx
    def find_by_regex(self, regex, search_regions=None):
        if search_regions is None:
            search_regions = self.regions
        find_by_name = regex.startswith("@")
        if find_by_name:
            regex = regex[1:]
        re_pattern = re.compile(regex)
        regions = []
        for region in search_regions:
            if find_by_name:
                name = region["name"]
            else:
                name = region["parent"]
            if re_pattern.match(name) is not None:
                regions.append(region)
        return regions

    # Find by selector
    def find_by_selector(self, selector, search_regions=None):
        if search_regions is None:
            search_regions = self.regions
        regions = []
        find_by_name = selector.startswith("@")
        if find_by_name:
            selector = selector[1:]
        find_child = selector.endswith(">")
        if find_child:
            selector = selector[:-1]
        find_all = selector.startswith(">")
        if find_all:
            selector = selector[1:]
        for region in search_regions:
            name = region["parent"]
            if find_by_name:
                name = region["name"]
            if find_all:
                if (find_child and selector+">" in name) or (not find_child and selector in name and selector+">" not in name):
                    regions.append(region)
            else:
                if (find_child and name.startswith(selector+">")) or (not find_child and name.startswith(selector) and selector+">" not in name):
                    regions.append(region)
        return regions

    # Find by selectors (list)
    def find_by_selectors(self, selector_list, search_regions=None):
        if type(selector_list) is str:
            selectors = selector_list.split("|")
            new_selectors = []
            for selector in selectors:
                new_selectors.append(selector)
            return self.find_by_selectors(new_selectors, search_regions)
        if search_regions is None:
            search_regions = self.regions
        regions = []
        for selector in selector_list:
            regions += self.find_by_selector(selector, search_regions)
        return regions

    # Find selector cover region
    def find_by_region(self, region, search_regions=None):
        if type(region) is int:
            return self.find_by_region([region, region], search_regions)
        if search_regions is None:
            search_regions = self.regions
        regions = []
        for node in search_regions:
            if node["begin"] <= region[0] and node["end"] >= region[1]:
                regions.append(node)
        return regions

    # Find selector inside region
    def find_inside_region(self, region, search_regions=None):
        if type(region) is int:
            return self.find_inside_region([region, region], search_regions)
        if search_regions is None:
            search_regions = self.regions
        regions = []
        for node in search_regions:
            if node["begin"] >= region[0] and node["end"] <= region[1]:
                regions.append(node)
        return regions

    # Get parse time
    def get_elapse_time(self):
        return self.elapse_time
