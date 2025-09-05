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
import re
import traceback
import sys

import _find_ksp_compiler  # noqa
from ksp_compiler import main, ParseException


if __name__ == "__main__":
    try:
        # Call the main function from ksp_compiler
        main()
    except ParseException as ex:
        print(">>> BEGIN Error", file=sys.stderr)
        message = ex.message
        message = message.split("\n\n", 1)[0].strip()  # Keep only the first paragraph
        message = re.sub(r" \(line \d+\)$", "", message)
        print(message, file=sys.stderr)
        if ex.line:
            print(f">>> Command: {ex.line.command}", file=sys.stderr)
            print(f">>> Location: {ex.line.filename}: {ex.line.lineno}", file=sys.stderr)
        print(">>> END Error", file=sys.stderr)
    except Exception as ex:
        print(">>> BEGIN Exception", file=sys.stderr)
        message = traceback.format_exc()
        print(message, file=sys.stderr)
        print(">>> END Exception", file=sys.stderr)