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
from inspect import cleandoc
from textwrap import indent

from config.constants import ItemType
from config.system_config import SystemConfig
from doc_item.doc_item_reader import DocItemReader
from util.file_util import replace_in_file
from vscode_generator.base_generator import BaseGenerator

log = logging.getLogger(__name__)


class SnippetGenerator(BaseGenerator):
    CALLBACK_TEMPLATE = cleandoc("""
    "on <<name>>": {
        "body": [
            "// ${1:<<one_line_description>>}",
            "on <<name>><<parameter>>",
            "    ${2:// your code here}",
            "end on"
        ],
        "description": "<<description>>",
        "prefix": "on <<name>>"
    }
    """)
    WIDGET_TEMPLATE = cleandoc("""
    "<<name>>": {
        "body": [
            "// ${1:<<one_line_description>>}",
            "declare <<name>> <<variable_name>><<index_name>><<parameter_list>>"
        ],
        "description": "<<description>>",
        "prefix": "on <<name>>"
    }
    """)

    @staticmethod
    def read_callbacks() -> str:
        """
        From the *.csv file read the callbacks and construct the JSON output.
        """
        #     "on ui_control": {
        #         "body": [
        #             "{ ${1:UI callback, executed whenever the user changes the respective UI element} }",
        #             "on ui_control(\\$${2:uiVariable})",
        #             "    ${3:{your code here\\}}",
        #             "end on"
        #         ],
        #         "description": "UI callback, executed whenever the user changes the respective UI element",
        #         "prefix": "on ui_control"
        #     },
        json_list = []
        with DocItemReader(ItemType.CALLBACK) as csv_reader:
            log.info(f"Read callbacks from {csv_reader.csv_file.as_posix()}")
            for doc_item in csv_reader:
                json = SnippetGenerator.CALLBACK_TEMPLATE
                json = json.replace("<<name>>", doc_item.name)
                json = json.replace("<<one_line_description>>", doc_item.description.replace("\n", " "))
                json = json.replace("<<parameter>>", doc_item.get_snippet_parameter())
                json = json.replace("<<description>>", doc_item.description.replace("\n", "\\n"))
                json = indent(json, "    ")
                json_list.append(json)
        return ",\n".join(json_list)

    @staticmethod
    def read_widgets() -> str:
        """
        From the *.csv file read the widgets and construct the JSON output.
        """
        #     "ui_table": {
        #         "body": [
        #             "declare ui_table %${1:array}[${2:colmns}](${3:width}, ${4:height}, ${5:range})"
        #         ],
        #         "description": "create a user interface switch",
        #         "prefix": "ui_table"
        #     },
        json_list = []
        with DocItemReader(ItemType.WIDGET) as csv_reader:
            log.info(f"Read widgets from {csv_reader.csv_file.as_posix()}")
            for doc_item in csv_reader:
                json = SnippetGenerator.WIDGET_TEMPLATE
                # <<variable_name>><<index_name>><<parameter_list>>
                json = json.replace("<<name>>", doc_item.name)
                json = json.replace("<<variable_name>>", doc_item.get_snippet_variable_name())
                json = json.replace("<<index_name>>", doc_item.get_snippet_index_name())
                json = json.replace("<<parameter_list>>", doc_item.get_snippet_parameter_list())
                json = json.replace("<<one_line_description>>", doc_item.description.replace("\n", " "))
                json = json.replace("<<description>>", doc_item.description.replace("\n", "\\n"))
                json = indent(json, "    ")
                json_list.append(json)
        return ",\n".join(json_list)

    @staticmethod
    def process():
        """
        Reads the snippets JSON file and replace <<category>> with the section list.
        """
        log.info(f"Modify {SystemConfig().snippets_json.as_posix()}")
        search_string = f'    "<<{ItemType.CALLBACK.category()}>>": null'
        replace_string = SnippetGenerator.read_callbacks()
        replace_in_file(SystemConfig().snippets_json, search_string, replace_string)
        search_string = f'    "<<{ItemType.WIDGET.category()}>>": null'
        replace_string = SnippetGenerator.read_widgets()
        replace_in_file(SystemConfig().snippets_json, search_string, replace_string)
