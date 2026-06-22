import sublime
import sublime_plugin
import json


class FormatJsonCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                s = self.view.substr(region)
                try:
                    # Parse and re-serialize with 4-space indentation
                    data = json.loads(s)
                    formatted = json.dumps(data, indent=4, sort_keys=True)
                    self.view.replace(edit, region, formatted)
                except ValueError as e:
                    sublime.error_message("Invalid JSON: " + str(e))


class FlattenJsonCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                s = self.view.substr(region)
                try:
                    # Parse and serialize with no spaces
                    data = json.loads(s)
                    flattened = json.dumps(data, separators=(',', ':'))
                    self.view.replace(edit, region, flattened)
                except ValueError as e:
                    sublime.error_message("Invalid JSON: " + str(e))
