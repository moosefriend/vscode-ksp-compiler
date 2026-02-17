# vscode-ksp-compiler

Visual Studio Code Extension for compiling NI KONTAKT(TM) Script Processor (KSP) scripts

## Features

### Compiler

Press F7 to compile the KSP script and copy it to clipboard:  
![Compile](images/compile.png)  
Note: The [SublimeKSP Compiler CLI](https://github.com/nojanath/SublimeKSP) is used here which is integrated as submodule at `vscode_extension/sublime_ksp`

### Syntax Check

On the fly syntax checking using the KSP Compiler:  
![Error Reporting](images/error_reporting.png)

### Syntax Highlighting

Syntax Highlighting including the extended syntax of the KSP Compiler:  
![Syntax Highlighting](images/syntax_highlighting.png)

### Outline View

Outline view of callbacks, functions and variables:  
![Outline View](images/outline_view.png)

### Snippets

Snippets for basic control statements, built-in callbacks, widgets, functions, commands:  
![Snippets](images/snippets.png)

### Autocompletion

Autocompletion for built-in callbacks, widgets, functions, commands, and variables:  
![Autocompletion](images/autocompletion.png)

### Documentation

Documentation on mouse hover:  
![Hover Documentation](images/hover_documentation.png)

### Find References/Definition

Find References and Go to Definition:  
![References](images/references.png)

## References

This project

* integrates the [SublimeKSP Compiler](https://github.com/nojanath/SublimeKSP) by [Jonathan Thompson](https://github.com/nojanath)
  which was forked from [Nils Liberg's official SublimeKSP plugin, v1.11](http://nilsliberg.se/ksp/) released under the [GPL v3.0 license](https://github.com/nojanath/SublimeKSP/blob/master/LICENSE)
* is highly inspired by the [Visual Studio Code Extension for NI KONTAKT Script Processor (KSP)](https://github.com/r-koubou/vscode-ksp) by
  [Hiroaki@R-Koubou](https://github.com/r-koubou) released under the [MIT license](https://github.com/r-koubou/vscode-ksp/blob/main/LICENSE)

## License

[GPL v3.0](LICENSE)

## Author

[MooseFriend](https://github.com/moosefriend)
