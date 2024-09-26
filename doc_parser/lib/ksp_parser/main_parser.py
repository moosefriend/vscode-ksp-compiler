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
import pkgutil
import re
import shutil
from importlib import import_module
from pathlib import Path
from typing import Optional, Any, Union

import pypdf._text_extraction._layout_mode._fixed_width_page
from pypdf import PageObject, PdfReader

from ksp_parser.item_parser import ItemParser
from ksp_parser.toc_parser import TocParser
from config.constants import ParserType
from config.system_config import SystemConfig
from util.format import headline
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class MainParser:
    PAGE_PATTERN = re.compile(f"{'<' * 20} (?:Table of Contents )?Page (\\d+) {'>' * 20}")
    """Pattern to find a page number"""

    # Internally used to get the body of a page
    _parts: list[str] = []

    def __init__(self):
        """
        Parse the text from a text file which has been converted from the KSP Reference Manual PDF file.
        """
        self.items: Optional[ItemParser] = None

    @staticmethod
    def fixed_char_width_hack(a, b) -> float:
        """
        Currently the original function pypdf._text_extraction._layout_mode._fixed_width_page returns a ZeroDivisionError.
        So return a fixed value here.
        """
        return 200.0

    @staticmethod
    def convert_to_text():
        """
        Convert the PDF file to text.
        """
        # Note: The original function pypdf._text_extraction._layout_mode._fixed_width_page.fixed_char_width returns
        # a ZeroDivisionError => Hack the code to return a fixed value
        pypdf._text_extraction._layout_mode._fixed_width_page.fixed_char_width.__code__ = MainParser.fixed_char_width_hack.__code__
        reader = PdfReader(SystemConfig().pdf_file)
        # If a page offset is specified then first scan the table of contents
        if SystemConfig().page_offset > 0:
            toc = "Table of Contents "
        else:
            toc = ""
        SystemConfig().txt_file_original.parent.mkdir(parents=True, exist_ok=True)
        with SystemConfig().txt_file_original.open("w", encoding='utf-8') as f:
            log.info(f"Convert PDF to TEXT: {SystemConfig().pdf_file} -> {SystemConfig().txt_file_original}")
            page_cnt = 0
            for page in reader.pages:
                f.write(f"{'<' * 20} {toc}Page {page_cnt + 1} {'>' * 20}\n")
                f.write(MainParser.get_body(page, toc))
                if page_cnt and page_cnt % 80 == 0:
                    print("")
                page_cnt += 1
                if toc and SystemConfig().page_offset == page_cnt:
                    page_cnt = 0
                    toc = ""
                print(".", end="")
            print("")
            log.info(f"{page_cnt} pages converted")
        if not SystemConfig().txt_file_fixed.is_file():
            log.info(f"Copy {SystemConfig().txt_file_original.as_posix()} -> {SystemConfig().txt_file_fixed.as_posix()}")
            shutil.copyfile(SystemConfig().txt_file_original, SystemConfig().txt_file_fixed)
            log.info(f"TODO: Manually fix the content of {SystemConfig().txt_file_fixed}")
        else:
            log.info(f"TODO: Update the content of {SystemConfig().txt_file_fixed}")

    def parse(self):
        """
        Parse the content of the text file.
        """
        with RewindReader(SystemConfig().txt_file_fixed, page_no_pattern=MainParser.PAGE_PATTERN) as reader:
            SystemConfig().reader = reader
            headline("Processing Table of Contents (TOC)")
            toc: TocParser = MainParser.get_parser(ParserType.TOC)
            toc.parse()
            if SystemConfig().dump:
                toc.dump()
            SystemConfig().toc = toc
            for parser_type in ParserType.all_phases():
                if SystemConfig().has_phase(parser_type):
                    headline(f"Processing {parser_type.plural()}")
                    self.items = MainParser.get_parser(parser_type)
                    self.items.parse()
                    self.items.export()
                    if SystemConfig().dump:
                        self.items.dump()

    @staticmethod
    def get_body(page: PageObject, toc: str) -> str:
        """
        Get the page body without header and footer.

        :param page: Page to scan read from PdfReader
        :param toc: If this contains a string then the page is in the table of contents
        :return: Page body
        """
        content = page.extract_text(extraction_mode="layout") + "\n"
        if not toc:
            # Remove the first lines from the exported text which represents the footer
            extract = content.split("\n", SystemConfig().page_header_lines)[SystemConfig().page_header_lines]
            content = extract
        return content

    @staticmethod
    def get_parser(parser_type: ParserType, *args, **kwargs) -> Union['MainParser', TocParser, ItemParser]:
        """
        Dynamically load a class to handle the parsing for the specified parser type of the Kontakt KSP manual
        depending on the Kontakt version.

        :param parser_type: ParserType to load the corresponding class
        :param args: Arguments for the constructor of the parser class
        :param kwargs: Keyword arguments for the constructor of the parser class
        :return: Concrete parser for the specified parser type depending on the specified Kontakt KSP manual version
        """
        return MainParser.load_parser(parser_type, SystemConfig().kontakt_version, *args, **kwargs)

    @staticmethod
    def load_parser(parser_type: ParserType, version: str, *args, **kwargs) -> Any:
        """
        Dynamically load a class to handle the parsing of the Kontakt KSP manual depending on the Kontakt version.

        :param parser_type: ParserType to load the corresponding class
        :param version: Kontakt manual version needed to select the right parser
        :param args: Arguments for the constructor of the parser class
        :param kwargs: Keyword arguments for the constructor of the parser class
        :return: Concrete parser for the specified parser type depending on the specified Kontakt KSP manual version
        """
        # Dynamically try to load a class matching Kontakt manual version
        parser_name = parser_type.value.lower()
        module_name = f"ksp_{version.replace('.', '_')}.ksp_{version.replace('.', '_')}_{parser_name}_parser"
        class_name = f"Ksp{parser_type.value}Parser"
        try:
            module = import_module(module_name)
            parser_class = getattr(module, class_name)
            parser = parser_class(version, *args, **kwargs)
        except ModuleNotFoundError:
            cur_major = version.split(".")[0]
            log.warning(f"No {parser_name} parser for Kontakt KSP manual version {version} found")
            log.info(f"=> Check if there is a {parser_name} parser for Kontakt KSP manual version {cur_major}.*")
            root_dir = Path(__file__).parent.parent
            cur_version = ""
            for importer, modname, is_pkg in pkgutil.iter_modules([root_dir.as_posix()]):
                if m := SystemConfig.KSP_PATTERN.match(modname):
                    major = m.group(1)
                    minor = m.group(2)
                    log.info(f"- Kontakt {major}.{minor}")
                    # Check if there is a parser for the same major version
                    # If so then take the latest parser for that major version
                    if cur_major == major:
                        cur_version = f"{major}.{minor}"
            if cur_version:
                log.info(f"FOUND => Use {parser_name} parser for Kontakt KSP manual version {cur_version} instead")
                parser = MainParser.load_parser(parser_type, cur_version, *args, **kwargs)
            else:
                log.info(f"=> No {parser_name} parser for Kontakt KSP manual version {cur_major}.* found")
                log.info(f"=> Fallback to base {parser_name} parser")
                module_name = f"ksp_parser.{parser_name}_parser"
                class_name = f"{parser_type.value}Parser"
                module = import_module(module_name)
                parser_class = getattr(module, class_name)
                parser = parser_class(*args, **kwargs)
        return parser


if __name__ == "__main__":
    # For testing only
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    headline("Loading main parser")
    root = Path(__file__).parent.parent.parent
    ini_file = root / "cfg" / "ksp_7_10" / "system.ini"
    config = SystemConfig(ini_file)
    parser = MainParser.get_parser(ParserType.MAIN)
    parser.parse()
