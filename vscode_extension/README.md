# Compiler
```
ksp_compiler.py [-h] [-c] [-v] [-e] [-o] [-t] [-d] source_file [output_file]

positional arguments:
  source_file
  output_file

optional arguments:
  -h, --help                               show this help message and exit
  -f, --force                              force all specified compiler options, overriding any compile_with pragma directives from the script
  -c, --compact                            remove indents in compiled code
  -v, --compact_variables                  shorten and obfuscate variable names in compiled code
  -d, --combine_callbacks                  combines duplicate callbacks - but not functions or macros
  -e, --extra_syntax_checks                additional syntax checks during compilation
  -o, --optimize                           optimize the compiled code
  -b, --extra_branch_optimization          adds branch optimization checks earlier in compile process, allowing define constant based branching etc.
  -l, --log                                dumps the compiler output to a log file on failed compilation
  -i NUM_SPACES, --indent-size NUM_SPACES  specifies how many spaces is used for indentation, if --compact compiler option is not used
  -t, --add_compile_date                   adds the date and time comment atop the compiled code
  -x, --sanitize_exit_command              adds a dummy no-op command before every exit function call


> python ksp_compiler.py --force -c -e -o "<source-file-path>" "<target-file-path>"
```