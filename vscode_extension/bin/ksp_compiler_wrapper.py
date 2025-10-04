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
import traceback
import sys

import _find_ksp_compiler  # noqa
from ksp_compiler import main, ParseException as OriginalParseException
import ksp_compiler

class PatchedParseException(OriginalParseException):
    """Patch the ParseException to save the clean message"""

    def __init__(self, line, message):
        """
        Patch the ParseException to save the clean message.

        :param line: Line object or None
        :param message: Error message
        """
        super().__init__(line, message)
        self.error_message = message.strip()


if __name__ == "__main__":
    exit_code = 0
    try:
        # Monkey patch the ParseException in ksp_compiler
        # This is needed to get the clean error message
        ksp_compiler.ParseException = PatchedParseException
        # Call the main function from ksp_compiler
        main()
    except PatchedParseException as ex:
        print(">>> BEGIN Error", file=sys.stderr)
        message = ex.error_message
        print(message, file=sys.stderr)
        if ex.line:
            print(f">>> Command: {ex.line.command}", file=sys.stderr)
            print(f">>> Location: {ex.line.filename}: {ex.line.lineno}", file=sys.stderr)
        print(">>> END Error", file=sys.stderr)
        exit_code = 1
    except Exception as ex:
        print(">>> BEGIN Exception", file=sys.stderr)
        message = traceback.format_exc()
        print(message, file=sys.stderr)
        print(">>> END Exception", file=sys.stderr)
        exit_code = -1
    sys.exit(exit_code)