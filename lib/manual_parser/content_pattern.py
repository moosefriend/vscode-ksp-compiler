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
from re import Pattern, Match
from typing import Optional


class ContentPattern:
    def __init__(self, start_pattern: Pattern, stop_pattern: Pattern):
        """
        Container for the start and stop patterns for searching content.

        :param start_pattern: Pattern to find the headline for the content start
        :param stop_pattern: Pattern to find the headline for the content end
        """
        self.start_pattern: Pattern = start_pattern
        """Pattern to find the headline for the content start"""
        self.stop_pattern: Pattern = stop_pattern
        """Pattern to find the headline for the content end"""

    def start(self, line: str) -> Optional[Match[str]]:
        """
        Check if the passed line matches the start pattern.

        :param line: Line to check
        :return: Match object or None if the line does not match the start pattern
        """
        return self.start_pattern.match(line)

    def stop(self, line: str) -> Optional[Match[str]]:
        """
        Check if the passed line matches the stop pattern.

        :param line: Line to check
        :return: Match object or None if the line does not match the stop pattern
        """
        return self.stop_pattern.match(line)
