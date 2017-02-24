# -*- encoding: utf-8 -*-

import sublime
import sublime_plugin
import os.path
from .sane_snippets_tools import Snippet, clean
from .functions import *

def plugin_loaded():
    sublime.run_command('generate_snippets')

class SaneSnippetListener(sublime_plugin.EventListener):

    def on_post_save(self, view):
        if not view.file_name().endswith('.sane-snippet'):
            return
        snippet = Snippet(view.file_name())
        snippet.convert(force=True)

class SaneSnippetsCommand(sublime_plugin.ApplicationCommand):

    def generate_action(self):

        for dirname, dirs, files in walk_tree(sublime.packages_path()):

            for file in files:
                if not file.endswith('.sane-snippet'):
                    continue

                Snippet(os.path.join(dirname, file)).convert(force=True)

    def clean_action(self):
        clean()

    def run(self, action, *args, **kwargs):
        try:
            function = getattr(self, action + '_action')
        except AttributeError:
            return sublime.error_message("SaneSnippet: "
                                         "Couldn't find the action '{}'".format(action))
        function(*args, **kwargs)
