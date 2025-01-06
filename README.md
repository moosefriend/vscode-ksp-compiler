# vscode-ksp-compiler
Visual Studio Code Extension for compiling NI KONTAKT(TM) Script Processor (KSP) scripts

Features:
* Integration of the [SublimeKSP Compiler](https://github.com/nojanath/SublimeKSP) as submodule `sublime_ksp`
* From that SublimeKSP project only the `compiler` is used (called at `subblime_ksp/compiler/ksp_compiler.py`)
* Extended Syntax of the KSP Compiler is supported
* The `doc_parser` scans the KSP manuals (*.pdf) provided by Native Instruments to generate
  autocompletion incl. documentation hints

## Parsing KSP Manuals (done)
The `doc_parser` is developed in Python.
As IDE for the Python script development it's recommended to use PyCharm.

Features:
* Convert *.pdf manual into a *.txt file (the *.txt file must be fixed manually)
* Parse the *.txt for table of content
* Parse the *.txt and generate *.csv for built-in callbacks
* Parse the *.txt and generate *.csv for built-in widgets
* Parse the *.txt and generate *.csv for built-in functions
* Parse the *.txt and generate *.csv for built-in commands
* Parse the *.txt and generate *.csv for built-in variables

For details check [doc_parser README.md](doc_parser/REAMDE.md).
 
## Visual Studio Code Extension (in progress)
* Read the *.csv files and generate the necessary TypeScript files (done)
* Provide patch files to override or add certain elements (done)
* Create tree view incl. icons for KSP scripts (*.ksp) (open)
* Create configuration settings for the KSP compiler (open)
* Call the compiler and copy the result into the clipboard (open)
* The generated code shall be copied to the clipboard so that it can be applied in the KONTAKT
  editor (open)

## References
This project
* integrates the [SublimeKSP Compiler](https://github.com/nojanath/SublimeKSP) by [Jonathan Thompson](https://github.com/nojanath)
  which was forked from [Nils Liberg's official SublimeKSP plugin, v1.11](http://nilsliberg.se/ksp/) released under the [GPL v3.0 license](https://github.com/nojanath/SublimeKSP/blob/master/LICENSE)
* is highly inspired from the [Visual Studio Code Extension for NI KONTAKT Script Processor (KSP)](https://github.com/r-koubou/vscode-ksp) by [Hiroaki@R-Koubou](https://github.com/r-koubou) released under the
  [MIT license](https://github.com/r-koubou/vscode-ksp/blob/main/LICENSE)

## License
* [GPL v3.0](LICENSE)

## Author
* [MooseFriend](https://github.com/moosefriend)