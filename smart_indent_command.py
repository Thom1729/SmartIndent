import sublime
import sublime_plugin

from sublime import Region

import re
from itertools import takewhile

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
        regions, levels = map(list, zip( *map(self.get_depth, lines) ))

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
                self.view.erase(edit, region)
            elif level is not None:
                self.view.replace(edit,
                    region,
                    '\t' * level
                )

    def get_depth(self, line):
        def scopes(point):
            return self.view.scope_name(point).strip().split(' ')

        text = self.view.substr(line)
        indent_width = len(text) - len(text.lstrip())

        begin = line.begin() + indent_width
        indent_region = Region(line.begin(), begin)

        parts = scopes(begin)

        r = begin
        while any(
            re.search(r'punctuation\..*\.end', s)
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

        if self.view.match_selector(line.begin(), 'string,comment'):
            return (indent_region, None)

        new_indent = len([
            part for part in parts
            if part.startswith('meta.')
        ])

        return (indent_region, new_indent)