/**
 * This file is part of the vscode-ksp-compiler distribution
 * (https://github.com/moosefriend/vscode-ksp-compiler).
 *
 * Copyright (c) 2024 MooseFriend (https://github.com/moosefriend)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */
import * as vscode from 'vscode';
import * as path from 'path';

import * as configkey from './configurationConstants';
import { ConfigurationManager } from './configurationManager';
import { EXTENSION_DIR } from './constants';

/**
 * Build a internal compiler's commandline option.
 * Initial value is set by user configuration.
 */
export class CompileBuilder {
    // Compile options
    public inputFile: string;
    public outputFile: string | undefined;
    public compiler_script: string;
    public compact: boolean = false;
    public obfuscate: boolean = false;
    public extra_syntax_check: boolean = false;
    public optimize: boolean = false;
    public compile_date: boolean = false;

    /**
     * Commandline options initialized by configuration
     */
    constructor(inputFile: string, outputFile = undefined) {
        this.compiler_script = ConfigurationManager.getConfig<string>(configkey.KEY_COMPILER_SCRIPT, "");
        this.inputFile = inputFile;
        this.outputFile = outputFile;
        this.compact = ConfigurationManager.getConfig<boolean>(configkey.KEY_COMPACT, false);
        this.obfuscate = ConfigurationManager.getConfig<boolean>(configkey.KEY_OBFUSCATE, false);
        this.extra_syntax_check = ConfigurationManager.getConfig<boolean>(configkey.KEY_EXTRA_SYNTAX_CHECK, false);
        this.optimize = ConfigurationManager.getConfig<boolean>(configkey.KEY_OPTIMIZE, false);
        this.compile_date = ConfigurationManager.getConfig<boolean>(configkey.KEY_COMPILE_DATE, false);
    }

    /**
     * Build a commandline option string
     */
    public build(): string[] {
        let args: string[] = [].concat(this.compiler_script);
        if (this.compact) {
            args.push("--compact");
        }
        if (this.obfuscate) {
            args.push("--compact_variables");
        }
        if (this.extra_syntax_check) {
            args.push("--extra_syntax_check");
        }
        if (this.optimize) {
            args.push("--optimize");
        }
        if (!this.compile_date) {
            args.push("--nocompiledate");
        }
        args.push(this.inputFile);
        if (this.outputFile) {
            args.push(this.outputFile);
        }
        return args;
    }
}
