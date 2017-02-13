# -*- encoding: utf-8 -*-

import sublime
import sublime_plugin
import os.path
from .sane_snippets_tools import generate_snippet, generate_snippets
from .functions import *

def plugin_loaded():
    pass

class SaneSnippet(sublime_plugin.EventListener):

    def on_post_save(self, view):
        file_name = view.file_name()
        if not file_name.endswith('.sane-snippet'):
            return
        rel_path = file_name.replace(sublime.packages_path(), '').strip(os.path.sep)
        package, folder, path = min_length(rel_path.split(os.path.sep, 2), 3)
        if folder is None:
            dst = os.path.splitext(file_name)[0] + '.sublime-snippet'
            generate_snippet(src=file_name, dst=dst)
        sublime.status_message("SaneSnippet: Generated '{}'".format(dst))
