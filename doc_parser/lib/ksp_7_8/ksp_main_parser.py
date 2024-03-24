#############################################################################
# This file is part of the vscode-ksp-compiler distribution
# (https://github.com/moosefriend/vscode-ksp-compiler).
import logging
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
from pathlib import Path

from pypdf import PageObject

from ksp_base.base_main_parser import BaseMainParser

log = logging.getLogger(__name__)


class KspMainParser(BaseMainParser):
    """Page ksp_parser for Kontakt 7.8 KSP reference manual"""

    def __init__(self, version: str, pdf_file: Path, out_dir: Path, delimiter: str):
        super().__init__(version, pdf_file, out_dir, delimiter, page_offset=8)

    @staticmethod
    def get_body(page: PageObject, page_no: int, toc: str) -> str:
        """
        Get the page body without header and footer.

        :param page: Page to scan read from PdfReader
        :param page_no: Page number in the PDF file
        :param toc: If this contains a string then the page is in the table of contents
        :return: Page body
        """
        content = page.extract_text(extraction_mode="layout") + "\n"
        if not toc:
            try:
                # Remove the first line which represents the footer
                extract = content.split("\n", 2)[2]
                content = extract
            except IndexError:
                log.error(f"Page {page_no}: Page does not have 2 elements (check page_offset):\n{content}")
        return content
