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
import re
from pathlib import Path

from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class BaseTocParser:
    TOC_START_PATTERN = re.compile(r"^(\d+\.\s+)?Table of Contents")
    """Pattern to find the headline of the table of contents"""
    TOC_END_PATTERN = re.compile(r"^(\d+\.\s+)?Disclaimer$")
    """Pattern to find the first string after the table of contents"""
    TOC_HEADLINE_PATTERN = re.compile(r"^(\d+\.\s+.+?)\s+\.+\s+(\d+)$")
    """Pattern to find a headline in the table of contents """
    TOC_CATEGORY_PATTERN = re.compile(r"^(.+?)\s+\.+\s+(\d+)$")
    """Pattern to find a headline in the table of contents"""

    def __init__(self, version: str, reader: RewindReader, verbose: bool = False):
        """
        Parse the table of contents for headlines and categories.

        :param version: Kontakt manual version needed to select the right parser
        :param reader: RewindReader to read from the Kontakt KSP reference text file
        :param verbose: If True then it prints each found headline and category
        """
        self.version: str = version
        self.reader: RewindReader = reader
        self.ksp_name: str = f"ksp_{version.replace('.', '_')}"
        self.cfg_version_dir: Path = Path(__file__).parent.parent.parent / "cfg" / self.ksp_name
        self.all_headlines: dict[str, int] = {}
        self.all_categories: dict[str, dict[str, int]] = {}
        self.headline_cnt: int = 0
        self.category_cnt: int = 0

    def parse(self):
        """
        Parse the text file for table of contents.
        """
        log.info(f"Parse headlines and categories in {self.reader.file}")
        self.search_toc_start()
        self.scan_toc()
        log.info(f"{self.headline_cnt} headlines found")
        log.info(f"{self.category_cnt} categories found")

    def search_toc_start(self):
        """
        Find the line where the table of content starts.
        """
        for line in self.reader:
            # Search for the table of content
            if self.TOC_START_PATTERN.match(line):
                log.debug(f"Found TOC Start ({self.reader.location()})")
                self.reader.rewind()
                break

    def scan_toc(self):
        """
        Scan the table of contents for headlines and categories.
        """
        last_headline: str = ""
        self.headline_cnt = 0
        self.category_cnt = 0
        for line in self.reader:
            # Check for the end of the table of contents
            if self.TOC_END_PATTERN.match(line):
                log.debug(f"Found TOC End ({self.reader.location()})")
                self.reader.rewind()
                break
            # Check for headline
            elif m := self.TOC_HEADLINE_PATTERN.match(line):
                log.debug(f"- Found TOC Headline: {m.group(1)} ({self.reader.location()})")
                self.all_headlines[m.group(1)] = m.group(2)
                self.headline_cnt += 1
                last_headline = m.group(1)
            # Check for category
            elif m := self.TOC_CATEGORY_PATTERN.match(line):
                log.debug(f"   - Found TOC Category: {m.group(1)} ({self.reader.location()})")
                if not last_headline:
                    raise AssertionError(f"No headline for category {m.group(1)} ({self.reader.location()})")
                if last_headline not in self.all_categories:
                    self.all_categories[last_headline] = {}
                self.all_categories[last_headline][m.group(1)] = m.group(2)
                self.category_cnt += 1
