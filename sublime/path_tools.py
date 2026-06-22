"""Copy the current file's path/name to the clipboard."""
import os
import sublime
import sublime_plugin


class CopyAbsolutePathCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        path = self.view.file_name()
        if not path:
            sublime.error_message("Buffer isn't saved yet.")
            return
        sublime.set_clipboard(path)
        self.view.window().status_message("Copied: " + path)


class CopyRelativePathCommand(sublime_plugin.TextCommand):
    """Copy the path relative to the nearest open project folder."""
    def run(self, edit):
        path = self.view.file_name()
        if not path:
            sublime.error_message("Buffer isn't saved yet.")
            return
        rel = path
        for folder in self.view.window().folders():
            if path.startswith(folder):
                rel = os.path.relpath(path, folder)
                break
        sublime.set_clipboard(rel)
        self.view.window().status_message("Copied: " + rel)


class CopyFileNameCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        path = self.view.file_name()
        if not path:
            sublime.error_message("Buffer isn't saved yet.")
            return
        name = os.path.basename(path)
        sublime.set_clipboard(name)
        self.view.window().status_message("Copied: " + name)
