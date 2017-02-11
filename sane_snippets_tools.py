# -*- encoding: utf-8 -*-

import xml.etree.ElementTree as ET
from textwrap import dedent
import sublime
import os
import re

SANE_EXTENSION = '.sane-snippet'

class SnippetConvertor:

    templates = {
        'xml': dedent("""\
                        <snippet>
                            <content><![CDATA[{content}]]></content>
                            <tabTrigger>{tabTrigger}</tabTrigger>
                            <scope>{scope}</scope>
                            <description>{description}</description>
                        </snippet>
                        """),
        'sane': dedent("""\
                        ---
                        description: {description}
                        tabTrigger:  {tabTrigger}
                        scope:       {scope}
                        ---
                        {content}
                        """)
    }

    re_sane = re.compile(r'---\n(?P<header>.*?)\n---\n(?P<content>.*)', re.DOTALL)
    re_sane_header_line = re.compile(r'^(?:(?P<comment>#.*)|(?P<key>[a-zA-Z]+): *(?P<value>.*))$')

    @classmethod
    def parse(cls, file):
        if file.endswith('.sane-snippet'):
            format_ = 'sane'
        elif file.endswith('.sublime-snippet'):
            format_ = 'xml'
        else:
            raise ValueError('Unknown file format')

        if format_ == 'xml':
            root = ET.parse(file).getroot()
            content = getattr(root.find('content'), 'text', '')
            if content.startswith('\n'):
                content = content[1:]
            if content.endswith('\n'):
                content = content[:-1]
            return {
                'content': content,
                'tabTrigger': getattr(root.find('tabTrigger'), 'text', ''),
                'scope': getattr(root.find('scope'), 'text', ''),
                'description': getattr(root.find('description'), 'text', ''),
            }
        elif format_ == 'sane':
            with open(file, 'r') as fp:
                matchobj = cls.re_sane.match(fp.read())
            header, content = matchobj.group('header'), matchobj.group('content')
            if content.endswith('\n'):
                content = content[:-1]

            infos = {}
            for line in header.splitlines():
                matchobj = cls.re_sane_header_line.match(line)
                if not matchobj or matchobj.group('comment'):
                    continue
                infos[matchobj.group('key')] = matchobj.group('value')

            return {
                'content': content,
                'tabTrigger': infos.get('tabTrigger', ''),
                'scope': infos.get('scope', ''),
                'description': infos.get('description', '')
            }

    @classmethod
    def stringify(cls, snippetobj, format_):
        return cls.templates[format_].format(**snippetobj)

def get_file_name(sane_snippet_path):
    name = os.path.basename(sane_snippet_path)
    return os.path.splitext(name)[0] + '.sublime-snippet'

def generate_sublime_snippet(sane_snippet_path, dst):
    snippetobj = SnippetConvertor.parse(os.path.join(sublime.packages_path(), sane_snippet_path))
    file_name = os.path.join(sublime.packages_path(), dst)
    if not os.path.exists(file_name):
        os.makedirs(file_name)
    file_name = os.path.join(file_name, get_file_name(sane_snippet_path))
    with open(file_name, 'w') as fp:
        fp.write(SnippetConvertor.stringify(snippetobj, 'xml'))

# def generate_sublime_snippets(snippet_folder, dst_folder):
#     for _, dirs, files in os.walk(snippet_folder):

def generate_sane_snippet(sublime_snippet_path, dst):
    """Convert a .sublime-snippet and write it at dst. Those two path must be absolute"""
    snippetobj = SnippetConvertor.parse(sublime_snippet_path)
    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))
    with open(dst, 'w', encoding='utf-8') as fp:
        fp.write(SnippetConvertor.stringify(snippetobj, 'sane'))

def generate_sane_snippets(sublime_snippet_path, dst_folder_name):
    """Used to migrate from normal snippet to sane snippets"""
    rel_path = lambda file: file[len(sublime_snippet_path):].strip(os.path.sep + '/')
    for root, dirs, files in os.walk(sublime_snippet_path):
        for file in files:
            if not file.endswith('.sublime-snippet'):
                continue
            src = os.path.join(root, file)
            dst = os.path.join(os.path.dirname(sublime_snippet_path), dst_folder_name,
                               rel_path(src))
            dst = dst[:-16] + '.sane-snippet'
            generate_sane_snippet(src, dst)
