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
    def get_format(cls, file):
        if file.endswith('.sane-snippet'):
            return 'sane'
        elif file.endswith('.sublime-snippet'):
            return 'xml'
        else:
            raise ValueError('Unknown file format')

    @classmethod
    def parse(cls, file, format_):
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
                'description': infos.get('description', ''),
            }

    @classmethod
    def stringify(cls, snippetobj, format_):
        return cls.templates[format_].format(**snippetobj)

def generate_snippet(src, dst):
    """Automatically detects if it has to convert it to a sane or sublime format"""
    format_ = SnippetConvertor.get_format(src)
    snippetobj = SnippetConvertor.parse(src, format_)
    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))
    with open(dst, 'w', encoding='utf-8') as fp:
        fp.write(SnippetConvertor.stringify(snippetobj, SnippetConvertor.get_format(dst)))

def generate_snippets(src_folder, dst_folder_name, action):
    """src_folder is an absolute path to the [sane] snippets folder,
       and dst_folder_name is the *name* of the destination folder"""
    if action not in ['convert', 'migrate']:
        raise ValueError("The 'action' is invalid: '{}'".format(action))

    rel_path = lambda file: file[len(src_folder):].strip(os.path.sep + '/')
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            if not file.endswith('.sane-snippet' if action == 'convert' else '.sublime-snippet'):
                continue
            src = os.path.join(root, file)
            dst = os.path.join(os.path.dirname(src_folder), dst_folder_name,
                               rel_path(src))
            if action == 'convert':
                dst = dst[:-13] + '.sublime-snippet'
            else:
                dst = dst[:-16] + '.sane-snippet'
            generate_snippet(src, dst)

# generate_sublime_snippets(os.path.join(sublime.packages_path(), 'User', 'sane-snippets'), 'snippets')
# generate_sane_snippets(os.path.join(sublime.packages_path(), 'User', 'original-snippets'), 'sane-snippets')
# generate_snippets(os.path.join(sublime.packages_path(), 'User', 'original-snippets'), 'sane-snippets', 'migrate')
# generate_snippets(os.path.join(sublime.packages_path(), 'User', 'sane-snippets'), 'snippets', 'convert')
