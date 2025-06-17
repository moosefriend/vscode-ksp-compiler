#############################################################################
# This file is part of the vscode-ksp-compiler distribution
# (https://github.com/moosefriend/vscode-ksp-compiler).
#
# Copyright (c) 2025 MooseFriend (https://github.com/moosefriend)
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

log = logging.getLogger(__name__)


def headline(text: str, level=1):
    """
    Logs a headline.

    :param text: Text of the headline
    :param level: level of the headline
    """
    match level:
        case 1:
            char = "#"
        case 2:
            char = "*"
        case 3:
            char = "-"
        case _:
            raise ValueError(f"Invalid level {level}: Only levels 1 to 3 are allowed")
    if level == 3:
        log.info(f"{char * 20} {text} {char * 20}")
    else:
        log.info(f"{char * 80}")
        for line in text.splitlines():
            log.info(f"{char} {line}")
        log.info(f"{char * 80}")


def log_step(text: str, prefix: str = ">>>>>"):
    """
    Logs a step headline.

    :param text: Text of the step
    :param prefix: Prefix to print before the step
    """
    log.info(f"{prefix} {text}")


def text2markdown(text: str) -> str:
    """
    Convert text to Markdown format by escaping special characters and replacing newlines with 2 spaces and newline.

    :param text: Text to convert
    :return: Converted text in Markdown format
    """
    # Replace special characters for Markdown compatibility using regex replace
    text = re.sub(r"([\\`*_{}\[\]()#+<>!~\-=:|])", r"\\\\\1", text)
    # Replace newlines with two spaces and newline
    text = text.replace("\n", "  \n")
    return text
