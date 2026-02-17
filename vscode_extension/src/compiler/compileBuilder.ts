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
import * as configkey from '../config/configurationConstants';
import { ConfigurationManager } from '../config/configurationManager';
import * as path from 'path';

/**
 * Build an compiler commandline options.
 * Initial value is set by user configuration.
 */
export class CompileBuilder {
    // Compile options
    public inputFile: string;
    public outputFile: string | undefined;
    public compiler_script: string;
    public force: boolean = false;
    public compact: boolean = false;
    public compact_variables: boolean = false;
    public combine_callbacks: boolean = false;
    public extra_syntax_check: boolean = false;
    public optimize: boolean = false;
    public extra_branch_optimization: boolean = false;
    public indent_size: number = 4;
    public add_compile_date: boolean = false;
    public sanitize_exit_command: boolean = false;

    /**
     * Commandline options initialized by configuration
     */
    constructor(inputFile: string, outputFile: string) {
        this.compiler_script = path.resolve(__dirname, '../../../bin/ksp_compiler_wrapper.py');
        this.inputFile = inputFile;
        this.outputFile = outputFile;
        this.force = ConfigurationManager.getConfig<boolean>(configkey.KEY_FORCE);
        this.compact = ConfigurationManager.getConfig<boolean>(configkey.KEY_COMPACT);
        this.compact_variables = ConfigurationManager.getConfig<boolean>(configkey.KEY_COMPACT_VARIABLES);
        this.combine_callbacks = ConfigurationManager.getConfig<boolean>(configkey.KEY_COMBINE_CALLBACKS);
        this.extra_syntax_check = ConfigurationManager.getConfig<boolean>(configkey.KEY_EXTRA_SYNTAX_CHECK);
        this.optimize = ConfigurationManager.getConfig<boolean>(configkey.KEY_OPTIMIZE);
        this.extra_branch_optimization = ConfigurationManager.getConfig<boolean>(configkey.KEY_EXTRA_BRANCH_OPTIMIZATION);
        this.indent_size = ConfigurationManager.getConfig<number>(configkey.KEY_INDENT_SIZE);
        this.add_compile_date = ConfigurationManager.getConfig<boolean>(configkey.KEY_ADD_COMPILE_DATE);
        this.sanitize_exit_command = ConfigurationManager.getConfig<boolean>(configkey.KEY_SANITIZE_EXIT_COMMAND);
    }

    /**
     * Build a commandline option string
     */
    public build(): string[] {
        let args: string[] = []
        args.push(this.compiler_script);
        if (this.force) {
            args.push("--force");
        }
        if (this.compact) {
            args.push("--compact");
        }
        if (this.compact_variables) {
            args.push("--compact_variables");
        }
        if (this.combine_callbacks) {
            args.push("--combine_callbacks");
        }
        if (this.extra_syntax_check) {
            args.push("--extra_syntax_check");
        }
        if (this.optimize) {
            args.push("--optimize");
        }
        if (this.extra_branch_optimization) {
            args.push("--extra_branch_optimization");
        }
        args.push("--indent-size");
        args.push(String(this.indent_size))
        if (this.add_compile_date) {
            args.push("--add_compile_date");
        }
        if (this.sanitize_exit_command) {
            args.push("--sanitize_exit_command");
        }
        args.push(this.inputFile);
        if (this.outputFile) {
            args.push(this.outputFile);
        }
        return args;
    }
}
