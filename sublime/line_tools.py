"""Line-oriented operations: sort+unique, dedup, reverse, sum numbers.

Operate on the selection, or the whole file if nothing is selected.
"""
import sublime
import sublime_plugin
import re


def _line_region(view):
    regions = [r for r in view.sel() if not r.empty()]
    if regions:
        # Expand each selection to full lines, return a single covering region.
        full = view.line(sublime.Region(regions[0].begin(), regions[-1].end()))
        return full
    return sublime.Region(0, view.size())


def _apply_lines(view, edit, fn):
    region = _line_region(view)
    lines = view.substr(region).split("\n")
    view.replace(edit, region, "\n".join(fn(lines)))


class SortUniqueLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def go(lines):
            seen = set()
            out = []
            for ln in sorted(lines):
                if ln not in seen:
                    seen.add(ln)
                    out.append(ln)
            return out
        _apply_lines(self.view, edit, go)


class RemoveDuplicateLinesCommand(sublime_plugin.TextCommand):
    """Drop duplicate lines while preserving original order."""
    def run(self, edit):
        def go(lines):
            seen = set()
            out = []
            for ln in lines:
                if ln not in seen:
                    seen.add(ln)
                    out.append(ln)
            return out
        _apply_lines(self.view, edit, go)


class ReverseLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        _apply_lines(self.view, edit, lambda lines: list(reversed(lines)))


class SumNumbersCommand(sublime_plugin.TextCommand):
    """Sum every number found in the selection; show the total in the status bar."""
    def run(self, edit):
        regions = [r for r in self.view.sel() if not r.empty()]
        if not regions:
            regions = [sublime.Region(0, self.view.size())]
        text = "\n".join(self.view.substr(r) for r in regions)
        nums = re.findall(r"-?\d+(?:\.\d+)?", text)
        total = sum(float(n) for n in nums)
        # Render as int when it's whole, else keep the decimal.
        pretty = int(total) if total == int(total) else total
        msg = "Sum of {0} numbers = {1}".format(len(nums), pretty)
        self.view.window().status_message(msg)
        sublime.set_clipboard(str(pretty))
