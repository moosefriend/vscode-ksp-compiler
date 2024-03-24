#############################################################################
# This file is part of the vscode-ksp-compiler distribution
# (https://github.com/moosefriend/vscode-ksp-compiler).

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
from doc_item.doc_item import DocItem


class CommandItem(DocItem):
    def __init__(self, name: str, description: str = None, source: str = None, signature: str = None, body: str = None):
        """
        Container for command documentation.

        :param name: Item name
        :param description: Item documentation
        :param source: Where the item has been parsed, e.g. build-in
        :param signature: Signature if the item is a function
        :param body: Snippet body
        """
        super().__init__(name, description, source, signature, body)
