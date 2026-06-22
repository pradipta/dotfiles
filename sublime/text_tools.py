"""Text transforms: Base64, URL encoding, JWT decoding, case conversion.

Each command operates on the non-empty selections; if nothing is selected it
falls back to the whole file (where that makes sense).
"""
import sublime
import sublime_plugin
import base64
import json
import re

try:
    from urllib.parse import quote, unquote
except ImportError:  # pragma: no cover - ST3 safety
    from urllib import quote, unquote


def _selections(view):
    """Return non-empty selections, or the whole buffer if none."""
    regions = [r for r in view.sel() if not r.empty()]
    if not regions:
        regions = [sublime.Region(0, view.size())]
    return regions


def _transform(view, edit, fn):
    for region in _selections(view):
        try:
            view.replace(edit, region, fn(view.substr(region)))
        except Exception as e:
            sublime.error_message("Transform failed: " + str(e))


class Base64EncodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        _transform(self.view, edit,
                   lambda s: base64.b64encode(s.encode("utf-8")).decode("ascii"))


class Base64DecodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def dec(s):
            s = s.strip()
            s += "=" * (-len(s) % 4)  # restore missing padding
            return base64.b64decode(s).decode("utf-8")
        _transform(self.view, edit, dec)


class UrlEncodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        _transform(self.view, edit, lambda s: quote(s, safe=""))


class UrlDecodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        _transform(self.view, edit, lambda s: unquote(s))


def _b64url_decode(segment):
    segment = segment.strip()
    segment += "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment.encode("ascii")).decode("utf-8")


class DecodeJwtCommand(sublime_plugin.TextCommand):
    """Decode the selected JWT into a new tab (header + payload). Non-destructive."""
    def run(self, edit):
        regions = [r for r in self.view.sel() if not r.empty()]
        if not regions:
            sublime.error_message("Select a JWT first.")
            return
        token = self.view.substr(regions[0]).strip()
        parts = token.split(".")
        if len(parts) < 2:
            sublime.error_message("That doesn't look like a JWT (need header.payload).")
            return
        try:
            header = json.loads(_b64url_decode(parts[0]))
            payload = json.loads(_b64url_decode(parts[1]))
        except Exception as e:
            sublime.error_message("Could not decode JWT: " + str(e))
            return
        out = "// HEADER\n" + json.dumps(header, indent=2, sort_keys=True)
        out += "\n\n// PAYLOAD\n" + json.dumps(payload, indent=2, sort_keys=True)
        view = self.view.window().new_file()
        view.set_scratch(True)
        view.set_name("JWT decoded")
        view.assign_syntax("Packages/JavaScript/JSON.sublime-syntax")
        view.run_command("append", {"characters": out})


def _to_words(s):
    """Split an identifier into lowercase words (handles camel/snake/kebab/space)."""
    s = re.sub(r"[\s_\-]+", " ", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)
    return [w for w in s.lower().split(" ") if w]


class ToSnakeCaseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        _transform(self.view, edit, lambda s: "_".join(_to_words(s)))


class ToKebabCaseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        _transform(self.view, edit, lambda s: "-".join(_to_words(s)))


class ToCamelCaseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def camel(s):
            words = _to_words(s)
            if not words:
                return s
            return words[0] + "".join(w.capitalize() for w in words[1:])
        _transform(self.view, edit, camel)
