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

    def migrate_action(self, soft=None):
        """Create .sane-snippet from .sublime-snippet
        if soft is None, then it'll ask each time the destination exists to overwrite it
        if soft is True, then it won't do anything if the destination already exists
        if soft is False, then it'll *silently* write the destination, even if it already exists
        """
        if soft not in (None, False, True):
            raise ValueError("The soft arguments should be None, False or True,"
                             "got {!r}".format(soft))

        for dirname, dirs, files in walk_tree(sublime.packages_path()):
            for file in files:
                if not file.endswith('.sublime-snippet'):
                    continue
                snippet = Snippet(os.path.join(dirname, file))
                if soft is True or soft is None:
                    try:
                        snippet.convert()
                    except FileExistsError:
                        if soft is None:
                            ans = sublime.yes_no_cancel_dialog(
                                "The file '{}' already exists. Overwrite?\n\n "
                                "(press cancel to stop everything)".format(snippet.get_dst()),
                                'Overwrite', 'Skip')
                            if ans == sublime.DIALOG_YES:
                                snippet.convert(force=True)
                            elif ans == sublime.DIALOG_NO:
                                continue
                            elif ans == sublime.DIALOG_CANCEL:
                                return

                elif soft is False:
                    snippet.convert(force=True)


    def run(self, action, *args, **kwargs):
        try:
            function = getattr(self, action + '_action')
        except AttributeError:
            return sublime.error_message("SaneSnippet: "
                                         "Couldn't find the action '{}'".format(action))
        function(*args, **kwargs)
