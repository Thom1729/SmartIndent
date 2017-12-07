import sublime
import sublime_plugin

from sublime import Region

import re
from itertools import takewhile

INDENT_LEVEL_SCOPES = r'^meta\.'
INDENT_LEVEL_SCOPES_IGNORE = r'^meta\.insert-snippet'
INDENT_ENDING_SCOPES = r'punctuation\..*\.end'

def gcp(*lists):
    s1 = min(lists)
    s2 = max(lists)

    for i, x in enumerate(s1):
        if x != s2[i]:
            return s1[:i]

    return s1

class SmartIndentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        lines = self.view.lines(Region(0, self.view.size()))

        levels = [ self.get_depth(line) for line in lines ]
        regions = [ self.get_indent(line) for line in lines ]

        for i in range(len(lines) - 1):
            if levels[i+1] > levels[i]:
                contents = list(takewhile(
                    lambda j: levels[j] > levels[i],
                    range(i+1, len(lines)),
                ))

                min_depth = min(levels[n] for n in contents)
                excess = min_depth - levels[i] - 1

                if excess:
                    for n in contents:
                        levels[n] -= excess

        for region, level in reversed(list(zip(regions, levels))):
            line = self.view.substr(self.view.line(region.begin()))

            if line == '' or line.isspace():
                level = 0

            if level is not None:
                old_indent = self.view.substr(region)
                new_indent = '\t' * level
                if new_indent != old_indent:
                    self.view.replace(edit, region, new_indent)

    def get_indent(self, line):
        text = self.view.substr(line)
        indent_width = len(text) - len(text.lstrip())

        begin = line.begin() + indent_width
        return Region(line.begin(), begin)

    def get_depth(self, line):
        def scopes(point):
            return self.view.scope_name(point).strip().split(' ')

        text = self.view.substr(line)
        indent_width = len(text) - len(text.lstrip())

        begin = line.begin() + indent_width

        parts = scopes(begin)

        r = begin
        while any(
            re.search(INDENT_ENDING_SCOPES, s)
            for s in parts
        ):
            r += 1
            parts = gcp(
                parts,
                scopes(r)
            )

        if line.begin() == 0:
            parts = []
        else:
            parts = gcp(
                parts,
                scopes(line.begin() - 1)
            )

        new_indent = len([
            part for part in parts
            if re.search(INDENT_LEVEL_SCOPES, part) and not
                re.search(INDENT_LEVEL_SCOPES_IGNORE, part)
        ])

        return new_indent
