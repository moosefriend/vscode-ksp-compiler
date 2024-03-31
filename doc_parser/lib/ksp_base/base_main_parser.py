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
import sys
from enum import Enum
from importlib import import_module
from pathlib import Path
from typing import Optional, Any

import pypdf._text_extraction._layout_mode._fixed_width_page
from pypdf import PageObject, PdfReader

from ksp_base.base_callback_parser import BaseCallbackParser
from ksp_base.base_command_parser import BaseCommandParser
from ksp_base.base_toc_parser import BaseTocParser
from ksp_base.base_widget_parser import BaseWidgetParser
from ksp_base.base_variable_parser import BaseVariableParser
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class ParserType(Enum):
    """
    Parser types used for dynamic loading.
    """
    MAIN = "Main"
    TOC = "Toc"
    CALLBACK = "Callback"
    WIDGET = "Widget"
    COMMAND = "Command"
    VARIABLE = "Variable"


class BaseMainParser:
    KSP_PATTERN = re.compile(r"^ksp_(\d+)_(\d+)$")
    """Pattern to find the Kontakt version specific parser"""
    PAGE_PATTERN = re.compile(f"{'<' * 20} (?:Table of Contents )?Page (\\d+) {'>' * 20}")
    """Pattern to find a page number"""

    # Internally used to get the body of a page
    _parts: list[str] = []

    def __init__(self, version: str, pdf_file: Path, out_dir: Path, delimiter: str, page_offset: int = 0, page_header_lines: int = 2):
        """
        Extract the text of a PDF file.

        :param version: Kontakt manual version needed to select the right parser
        :param pdf_file: PDF file name to read
        :param out_dir: Output directory e.g. for the exported *.csv files
        :param delimiter: CSV delimiter
        :param page_offset: The page number is decreased by this offset, e.g. if the page numbers start again with 1
            after the table of contents
        :param page_header_lines: Number of lines to skip from the beginning of each page (only for non table of content pages).
            This is needed to skip the header which is in the exported text in the beginning of the page.
        """
        self.version: str = version
        self.ksp_name: str = f"ksp_{version.replace('.', '_')}"
        self.pdf_file: Path = pdf_file
        self.out_dir: Path = out_dir
        self.delimiter: str = delimiter
        self.page_offset: int = page_offset
        self.page_header_lines: int = page_header_lines
        self.out_version_dir: Path = self.out_dir / self.ksp_name
        self.out_version_dir.mkdir(parents=True, exist_ok=True)
        self.cfg_version_dir: Path = Path(__file__).parent.parent.parent / "cfg" / self.ksp_name
        # Note: As extension here *.py is used, so that file links in the output will open in PyCharm in the internal editor
        self.txt_file: Path = self.out_version_dir / "KSP_Reference_Manual.txt.py"
        self.callbacks_csv: Path = self.out_version_dir / "built_in_callbacks.csv"
        self.widgets_csv: Path = self.out_version_dir / "built_in_widgets.csv"
        self.commands_csv: Path = self.out_version_dir / "built_in_commands.csv"
        self.variables_csv: Path = self.out_version_dir / "built_in_variables.csv"
        self.reader: Optional[RewindReader] = None
        self.toc: Optional[BaseTocParser] = None
        self.callbacks: Optional[BaseCallbackParser] = None
        self.widgets: Optional[BaseWidgetParser] = None
        self.commands: Optional[BaseCommandParser] = None
        self.variables: Optional[BaseVariableParser] = None

    @staticmethod
    def get_parser(parser_type: ParserType, version: str, *args, **kwargs) -> Any:
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
        module_name = f"ksp_{version.replace('.', '_')}.ksp_{parser_name}_parser"
        class_name = f"Ksp{parser_type.value}Parser"
        try:
            module = import_module(module_name)
            parser_class = getattr(module, class_name)
            parser = parser_class(version, *args, **kwargs)
        except ModuleNotFoundError:
            cur_major = version.split(".")[0]
            log.warning(f"No {parser_name} parser for Kontakt KSP manual version {version} found")
            log.info(f"=> Check if there is a {parser_name} parser for Kontakt KSP manual version {cur_major}.*:")
            root_dir = Path(__file__).parent.parent
            cur_version = ""
            for importer, modname, is_pkg in pkgutil.iter_modules([root_dir.as_posix()]):
                if m := BaseMainParser.KSP_PATTERN.match(modname):
                    major = m.group(1)
                    minor = m.group(2)
                    log.info(f"- Kontakt {major}.{minor}")
                    # Check if there is a parser for the same major version
                    # If so then take the latest parser for that major version
                    if cur_major == major:
                        cur_version = f"{major}.{minor}"
            if cur_version:
                log.info(f"FOUND => Use {parser_name} parser for Kontakt KSP manual version {cur_version} instead")
                parser = BaseMainParser.get_parser(parser_type, cur_version, *args, **kwargs)
            else:
                log.fatal(f"No {parser_name} parser for Kontakt KSP manual version {cur_major}.* found\n" +
                          f"=> Please implement the class {class_name} at {root_dir.as_posix()}/{module_name}.py")
                sys.exit(-1)
        return parser

    @staticmethod
    def fixed_char_width_hack(a, b) -> float:
        """
        Currently the original function pypdf._text_extraction._layout_mode._fixed_width_page returns a ZeroDivisionError.
        So return a fixed value here.
        """
        return 200.0

    def convert_to_text(self):
        """
        Convert the PDF file to text.
        """
        # Note: The original function pypdf._text_extraction._layout_mode._fixed_width_page.fixed_char_width returns
        # a ZeroDivisionError => Hack the code to return a fixed value
        pypdf._text_extraction._layout_mode._fixed_width_page.fixed_char_width.__code__ = BaseMainParser.fixed_char_width_hack.__code__
        reader = PdfReader(self.pdf_file)
        # If a page offset is specified then first scan the table of contents
        if self.page_offset > 0:
            toc = "Table of Contents "
        else:
            toc = ""
        with open(self.txt_file, "w", encoding='utf-8') as f:
            log.info(f"Convert PDF to TEXT: {self.pdf_file} -> {self.txt_file}")
            page_cnt = 0
            for page in reader.pages:
                f.write(f"{'<' * 20} {toc}Page {page_cnt + 1} {'>' * 20}\n")
                f.write(self.get_body(page, toc))
                if page_cnt and page_cnt % 80 == 0:
                    print("")
                page_cnt += 1
                if toc and self.page_offset == page_cnt:
                    page_cnt = 0
                    toc = ""
                print(".", end="")
            print("")
            log.info(f"{page_cnt} pages converted")

    def parse(self):
        """
        Parse the content of the text file.
        """
        with RewindReader(self.txt_file, page_no_pattern=BaseMainParser.PAGE_PATTERN) as self.reader:
            self.toc = BaseMainParser.get_parser(ParserType.TOC, self.version, self.reader)
            self.toc.parse()
            log.info("-" * 80)
            self.callbacks: BaseCallbackParser = BaseMainParser.get_parser(
                ParserType.CALLBACK,
                self.version,
                self.toc,
                self.reader,
                self.callbacks_csv,
                self.delimiter,
                self.page_offset
            )
            self.callbacks.parse()
            self.callbacks.export()
            # log.info("-" * 80)
            # self.widgets: BaseWidgetParser = BaseMainParser.get_parser(
            #     ParserType.WIDGET,
            #     self.version,
            #     self.toc,
            #     self.reader,
            #     self.widgets_csv,
            #     self.delimiter,
            #     self.page_offset
            # )
            # self.widgets.parse()
            # self.widgets.export()
            # log.info("-" * 80)
            # self.commands: BaseCommandParser = BaseMainParser.get_parser(
            #     ParserType.COMMAND,
            #     self.version,
            #     self.toc,
            #     self.reader,
            #     self.commands_csv,
            #     self.delimiter,
            #     self.page_offset
            # )
            # self.commands.parse()
            # self.commands.export()
            log.info("-" * 80)
            self.variables: BaseVariableParser = BaseMainParser.get_parser(
                ParserType.VARIABLE,
                self.version,
                self.toc,
                self.reader,
                self.variables_csv,
                self.delimiter,
                self.page_offset
            )
            self.variables.parse()
            self.variables.export()

    def get_body(self, page: PageObject, toc: str) -> str:
        """
        Get the page body without header and footer.

        :param page: Page to scan read from PdfReader
        :param toc: If this contains a string then the page is in the table of contents
        :return: Page body
        """
        content = page.extract_text(extraction_mode="layout") + "\n"
        if not toc:
            # Remove the first lines from the exported text which represents the footer
            extract = content.split("\n", self.page_header_lines)[self.page_header_lines]
            content = extract
        return content


if __name__ == "__main__":
    # For testing only
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    root = Path(__file__).parent.parent.parent
    out_dir = root / "out"
    version = "7.8"
    pdf_file = root / "in" / "KSP_Reference_7_8_Manual_en.pdf"
    reader = PdfReader(pdf_file)
    parser = BaseMainParser.get_parser(ParserType.MAIN, version, pdf_file, out_dir, ";")
    # parser.convert_to_text()
    parser.parse()
