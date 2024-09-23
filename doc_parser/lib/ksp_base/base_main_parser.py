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
from typing import Optional, Any

import pypdf._text_extraction._layout_mode._fixed_width_page
from pypdf import PageObject, PdfReader

from ksp_base.base_callback_parser import BaseCallbackParser
from ksp_base.base_command_parser import BaseCommandParser
from ksp_base.base_function_parser import BaseFunctionParser
from ksp_base.base_toc_parser import BaseTocParser
from ksp_base.base_widget_parser import BaseWidgetParser
from ksp_base.base_variable_parser import BaseVariableParser
from ksp_base.constants import ParserType
from ksp_base.system_config import SystemConfig
from util.rewind_reader import RewindReader

log = logging.getLogger(__name__)


class BaseMainParser:
    PAGE_PATTERN = re.compile(f"{'<' * 20} (?:Table of Contents )?Page (\\d+) {'>' * 20}")
    """Pattern to find a page number"""

    # Internally used to get the body of a page
    _parts: list[str] = []

    def __init__(self):
        """
        Parse the text from a text file which has been converted from the KSP Reference Manual PDF file.
        """
        self.callbacks: Optional[BaseCallbackParser] = None
        self.widgets: Optional[BaseWidgetParser] = None
        self.functions: Optional[BaseFunctionParser] = None
        self.commands: Optional[BaseCommandParser] = None
        self.variables: Optional[BaseVariableParser] = None

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
        pypdf._text_extraction._layout_mode._fixed_width_page.fixed_char_width.__code__ = BaseMainParser.fixed_char_width_hack.__code__
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
                f.write(BaseMainParser.get_body(page, toc))
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
        with RewindReader(SystemConfig().txt_file_fixed, page_no_pattern=BaseMainParser.PAGE_PATTERN) as reader:
            SystemConfig().reader = reader
            toc = BaseMainParser.get_toc_parser()
            toc.parse()
            SystemConfig().toc = toc
            log.info("-" * 80)
            version = SystemConfig().kontakt_version
            self.callbacks: BaseCallbackParser = BaseMainParser.get_callback_parser()
            self.callbacks.parse()
            self.callbacks.export()
            # self.callbacks.dump()
            log.info("-" * 80)
            self.widgets: BaseWidgetParser = BaseMainParser.get_widget_parser()
            self.widgets.parse()
            self.widgets.export()
            # self.widgets.dump()
            log.info("-" * 80)
            self.functions: BaseFunctionParser = BaseMainParser.get_function_parser()
            self.functions.parse()
            self.functions.export()
            # self.functions.dump()
            log.info("-" * 80)
            self.commands: BaseCommandParser = BaseMainParser.get_command_parser()
            self.commands.parse()
            self.commands.export()
            # self.commands.dump()
            log.info("-" * 80)
            self.variables: BaseVariableParser = BaseMainParser.get_variable_parser()
            self.variables.parse()
            self.variables.export()
            # self.variables.dump()

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
    def get_main_parser(*args, **kwargs) -> 'BaseMainParser':
        """
        Dynamically load a class to handle the main parsing of the Kontakt KSP manual depending on the Kontakt version.

        :param args: Arguments for the constructor of the parser class
        :param kwargs: Keyword arguments for the constructor of the parser class
        :return: Concrete parser for the specified parser type depending on the specified Kontakt KSP manual version
        """
        return BaseMainParser.load_parser(ParserType.MAIN, SystemConfig().kontakt_version, *args, **kwargs)

    @staticmethod
    def get_toc_parser(*args, **kwargs) -> BaseTocParser:
        """
        Dynamically load a class to handle the toc parsing of the Kontakt KSP manual depending on the Kontakt version.

        :param args: Arguments for the constructor of the parser class
        :param kwargs: Keyword arguments for the constructor of the parser class
        :return: Concrete parser for the specified parser type depending on the specified Kontakt KSP manual version
        """
        return BaseMainParser.load_parser(ParserType.TOC, SystemConfig().kontakt_version, *args, **kwargs)

    @staticmethod
    def get_callback_parser(*args, **kwargs) -> BaseCallbackParser:
        """
        Dynamically load a class to handle the callback parsing of the Kontakt KSP manual depending on the Kontakt version.

        :param args: Arguments for the constructor of the parser class
        :param kwargs: Keyword arguments for the constructor of the parser class
        :return: Concrete parser for the specified parser type depending on the specified Kontakt KSP manual version
        """
        return BaseMainParser.load_parser(ParserType.CALLBACK, SystemConfig().kontakt_version, *args, **kwargs)

    @staticmethod
    def get_widget_parser(*args, **kwargs) -> BaseWidgetParser:
        """
        Dynamically load a class to handle the widget parsing of the Kontakt KSP manual depending on the Kontakt version.

        :param args: Arguments for the constructor of the parser class
        :param kwargs: Keyword arguments for the constructor of the parser class
        :return: Concrete parser for the specified parser type depending on the specified Kontakt KSP manual version
        """
        return BaseMainParser.load_parser(ParserType.WIDGET, SystemConfig().kontakt_version, *args, **kwargs)

    @staticmethod
    def get_function_parser(*args, **kwargs) -> BaseFunctionParser:
        """
        Dynamically load a class to handle the function parsing of the Kontakt KSP manual depending on the Kontakt version.

        :param args: Arguments for the constructor of the parser class
        :param kwargs: Keyword arguments for the constructor of the parser class
        :return: Concrete parser for the specified parser type depending on the specified Kontakt KSP manual version
        """
        return BaseMainParser.load_parser(ParserType.FUNCTION, SystemConfig().kontakt_version, *args, **kwargs)

    @staticmethod
    def get_command_parser(*args, **kwargs) -> BaseCommandParser:
        """
        Dynamically load a class to handle the command parsing of the Kontakt KSP manual depending on the Kontakt version.

        :param args: Arguments for the constructor of the parser class
        :param kwargs: Keyword arguments for the constructor of the parser class
        :return: Concrete parser for the specified parser type depending on the specified Kontakt KSP manual version
        """
        return BaseMainParser.load_parser(ParserType.COMMAND, SystemConfig().kontakt_version, *args, **kwargs)

    @staticmethod
    def get_variable_parser(*args, **kwargs) -> BaseVariableParser:
        """
        Dynamically load a class to handle the variable parsing of the Kontakt KSP manual depending on the Kontakt version.

        :param args: Arguments for the constructor of the parser class
        :param kwargs: Keyword arguments for the constructor of the parser class
        :return: Concrete parser for the specified parser type depending on the specified Kontakt KSP manual version
        """
        return BaseMainParser.load_parser(ParserType.VARIABLE, SystemConfig().kontakt_version, *args, **kwargs)

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
                parser = BaseMainParser.load_parser(parser_type, cur_version, *args, **kwargs)
            else:
                log.info(f"No {parser_name} parser for Kontakt KSP manual version {cur_major}.* found\n" +
                         f"=> Fallback to base parser")
                module_name = f"ksp_base.base_{parser_name}_parser"
                class_name = f"Base{parser_type.value}Parser"
                module = import_module(module_name)
                parser_class = getattr(module, class_name)
                parser = parser_class(*args, **kwargs)
        return parser


if __name__ == "__main__":
    # For testing only
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    root = Path(__file__).parent.parent.parent
    ini_file = root / "cfg" / "ksp_7_10" / "system.ini"
    config = SystemConfig(ini_file)
    log.info(SystemConfig().kontakt_version)
    parser = BaseMainParser.get_main_parser()
    parser.parse()