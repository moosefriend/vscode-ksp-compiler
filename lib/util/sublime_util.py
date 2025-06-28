#############################################################################
# This file is part of the vscode-ksp-compiler distribution
# (https://github.com/moosefriend/vscode-ksp-compiler).
#
# Copyright (c) 2024 MooseFriend (https://github.com/moosefriend)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##############################################################################
import logging

import yaml
from typing import Any
from pathlib import Path

log = logging.getLogger(__name__)


class Sublime2TextMateConverter:
    """
    Converts a Sublime Text syntax definition file to a TextMate grammar file.
    """

    def __init__(self, sublime_syntax_file: Path, text_mate_file: Path):
        """
        Initialize the converter with paths to the Sublime syntax file and the TextMate grammar file.

        :param sublime_syntax_file: Path to the Sublime syntax file (usually with .sublime-syntax extension)
        :param text_mate_file: Path to the TextMate grammar file (usually with .tmGrammar.yml extension)
        """
        self.sublime_syntax_file: Path = sublime_syntax_file
        self.text_mate_file: Path = text_mate_file
        self.sublime_yaml: dict[str, Any] = self.load_sublime_yaml()
        self.text_mate_yaml: dict[str, Any] = {}

    def load_sublime_yaml(self):
        """
        Load the Sublime YAML syntax file.

        :return: Parsed YAML content as a dictionary
        """
        with self.sublime_syntax_file.open('r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def save_text_mate_yaml(self):
        """
        Save the TextMate YAML syntax file.
        """
        with self.text_mate_file.open('w', encoding='utf-8') as f:
            yaml.dump(self.text_mate_yaml, f, sort_keys=False, allow_unicode=True)

    @staticmethod
    def convert(sublime_syntax_file: Path, text_mate_file: Path):
        """
        Convert a Sublime syntax file to a TextMate grammar file.

        :param sublime_syntax_file: Path to the Sublime syntax file
        :param text_mate_file: Path to the TextMate grammar file
        """
        log.info(f"Convert {sublime_syntax_file.as_posix()} -> {text_mate_file.as_posix()}")
        converter = Sublime2TextMateConverter(sublime_syntax_file, text_mate_file)
        converter.sublime_to_textmate()
        converter.save_text_mate_yaml()

    def sublime_to_textmate(self):
        """
        Convert the loaded Sublime YAML syntax to TextMate format.
        """
        # Copy top-level keys
        for key in ['name', 'scope', 'scopeName', 'file_extensions', 'fileTypes', 'first_line_match', 'comment']:
            if key in self.sublime_yaml:
                self.text_mate_yaml[key if key != 'scope' else 'scopeName'] = self.sublime_yaml[key]
        # Patterns
        self.text_mate_yaml['patterns']: list[dict[str, Any]] = []
        if 'contexts' in self.sublime_yaml:
            repository: dict[str, Any] = {}
            for ctx_name, ctx_patterns in self.sublime_yaml['contexts'].items():
                repo_patterns: list[dict[str, Any]] = []
                for pat in ctx_patterns:
                    tm_pat: dict[str, Any] = {}
                    # Map Sublime YAML keys to TextMate
                    if 'match' in pat:
                        tm_pat['match'] = pat['match']
                    if 'scope' in pat:
                        tm_pat['name'] = pat['scope']
                    if 'push' in pat:
                        tm_pat['push'] = pat['push']
                    if 'set' in pat:
                        tm_pat['set'] = pat['set']
                    if 'include' in pat:
                        tm_pat['include'] = f"#{pat['include']}"
                    if 'begin' in pat:
                        tm_pat['begin'] = pat['begin']
                    if 'end' in pat:
                        tm_pat['end'] = pat['end']
                    if 'captures' in pat:
                        tm_pat['captures'] = pat['captures']
                    if 'begin_captures' in pat:
                        tm_pat['beginCaptures'] = pat['begin_captures']
                    if 'end_captures' in pat:
                        tm_pat['endCaptures'] = pat['end_captures']
                    if tm_pat:
                        repo_patterns.append(tm_pat)
                repository[ctx_name] = {'patterns': repo_patterns}
                # Add top-level patterns for main context
                if ctx_name == 'main':
                    self.text_mate_yaml['patterns'] = repo_patterns
            self.text_mate_yaml['repository'] = repository
