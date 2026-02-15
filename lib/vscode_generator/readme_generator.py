#############################################################################
# This file is part of the vscode-ksp-compiler distribution
# (https://github.com/moosefriend/vscode-ksp-compiler).
#
# Copyright (c) 2026 MooseFriend (https://github.com/moosefriend)
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

from config.system_config import SystemConfig
log = logging.getLogger(__name__)


class ReadmeGenerator:
    IMAGE_PATTERN = re.compile(r'^(.*?!\[[^]]*]\()(images/.*)$')

    @staticmethod
    def process():
        """
        Reads the local readme and generate a packaging readme to fix the links to images.
        """
        log.info(f"Generate {SystemConfig().readme_packaging.as_posix()}")
        with SystemConfig().readme_local.open(encoding="utf-8") as input_file:
            prefix = SystemConfig().readme_packaging.parent.name + "/"
            with SystemConfig().readme_packaging.open("w", encoding="utf-8") as output_file:
                output_file.write(f"<!-- DON'T EDIT THIS FILE!! It's generated from {SystemConfig().readme_local}! -->\n")
                # Replace Markdown image links:
                # from: ![alt](images/xxx.png)
                # to:   ![alt](vscode_extension/images/xxx.png)
                for line in input_file:
                    if m := ReadmeGenerator.IMAGE_PATTERN.match(line):
                        line = m.group(1) + prefix + m.group(2) + "\n"
                    output_file.write(line)
