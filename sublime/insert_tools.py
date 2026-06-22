"""Insert generators: UUID, ISO-8601 timestamp, Unix epoch."""
import sublime_plugin
import uuid
import datetime


def _insert(view, edit, text):
    for region in view.sel():
        view.replace(edit, region, text)


class InsertUuidCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        _insert(self.view, edit, str(uuid.uuid4()))


class InsertIsoTimestampCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        now = datetime.datetime.now(datetime.timezone.utc)
        _insert(self.view, edit, now.isoformat())


class InsertEpochCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        now = datetime.datetime.now(datetime.timezone.utc)
        _insert(self.view, edit, str(int(now.timestamp())))
