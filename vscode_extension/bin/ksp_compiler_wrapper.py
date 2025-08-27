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
import os

import _find_ksp_compiler  # noqa
from ksp_compiler import main, ParseException, KSPCompiler


def do_compile(code,
               remove_preprocessor_vars  = False,
               compact                   = True,
               compact_variables         = False,
               combine_callbacks         = True,
               extra_syntax_checks       = True,
               optimize                  = False,
               add_compiled_date_comment = False):

    compiler = KSPCompiler(code,
                           os.path.dirname(__file__),
                           compact                   = compact,
                           compact_variables         = compact_variables,
                           combine_callbacks         = combine_callbacks,
                           extra_syntax_checks       = extra_syntax_checks,
                           optimize                  = optimize,
                           add_compiled_date_comment = add_compiled_date_comment)
    compiler.compile()
    output_code = compiler.compiled_code

    if remove_preprocessor_vars and optimize == False:
        output_code = output_code.split('\n')
        del output_code[1:6]
        output_code = '\n'.join(output_code)

    output_code = output_code.replace('\r', '')

    return output_code

def test1():
    code = '''
        on init
            declare ~x := 5 * 2.333
            message(~x)
        end on'''
    do_compile(code, extra_syntax_checks=True, optimize=True)

if __name__ == "__main__":
    test1()
    exit(0)
    try:
        # Call the main function from ksp_compiler
        main()
    except ParseException as ex:
        raise
        # Handle the ParseException and print the error message
        msg = ex.message.strip()
        message, content, location = msg.rsplit('\n\n', 2)
        print(f"*** Error: {message.strip()} at {location}")

