# vscode-ksp-compiler
Visual Studio Code Extension for compiling NI KONTAKT(TM) Script Processor (KSP) scripts

Features:
* Integration of the [SublimeKSP Compiler](https://github.com/nojanath/SublimeKSP) as submodule `sublime_ksp`
* From that SublimeKSP project only the `compiler` is used (called at `subblime_ksp/compiler/ksp_compiler.py`)
* Extended Syntax of the KSP Compiler is supported
* The `doc_parser` scans the KSP manuals (*.pdf) provided by Native Instruments to generate
  autocompletion incl. documentation hints

# Status
## Parsing the KSP manuals (done)
Currently, the `doc_parser` is developed using Python.
As IDE for the Python script development it's recommended to use PyCharm Community Edition.
* Convert *.pdf manual into a *.txt file (done)
* Parse the *.txt for table of content (done)
* Parse the *.txt and generate *.csv for built-in callbacks (done)
* Parse the *.txt and generate *.csv for built-in widgets (done)
* Parse the *.txt and generate *.csv for built-in functions (done)
* Parse the *.txt and generate *.csv for built-in commands (done)
* Parse the *.txt and generate *.csv for built-in variables (done)
 
## Parsing external libraries (open)
* Parse Koala library and generate *.csv for variables and functions incl. their documentation (open)

## Visual Studio Code Extension (planned)
* Read the *.csv files and generate the necessary TypeScript files (open)
* Create tree view incl. icons for KSP scripts (*.ksp) (open)
* Create configuration settings for the KSP compiler (open)
* Call the compiler and copy the result into the clipboard (open)
* The generated code shall be copied to the clipboard so that it can be applied in the KONTAKT
  editor (open)

# References
This project
* integrates the [SublimeKSP Compiler](https://github.com/nojanath/SublimeKSP) by [Jonathan Thompson](https://github.com/nojanath)
  which was forked from [Nils Liberg's official SublimeKSP plugin, v1.11](http://nilsliberg.se/ksp/) released under the [GPL v3.0 license](https://github.com/nojanath/SublimeKSP/blob/master/LICENSE)
* is highly inspired from the [Visual Studio Code Extension for NI KONTAKT Script Processor (KSP)](https://github.com/r-koubou/vscode-ksp) by [Hiroaki@R-Koubou](https://github.com/r-koubou) released under the
  [MIT license](https://github.com/r-koubou/vscode-ksp/blob/main/LICENSE)

# License
* [GPL v3.0](LICENSE)

# Author
* [MooseFriend](https://github.com/moosefriend)