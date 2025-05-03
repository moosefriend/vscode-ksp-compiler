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
import vscode = require('vscode');

import * as tmp from 'tmp';
import * as fs from 'fs';
import * as path from 'path';
import * as child_process from 'child_process';
import { ThrottledDelayer } from '../lib/async';
import * as config from '../config/configurationConstants';
import { ConfigurationManager } from '../config/configurationManager';
import { CompileBuilder } from './compileBuilder';
import { exit } from 'process';

const REGEX_PARSER_MESSAGE_NEWLINE: RegExp = /[\r]?\n/;
const REGEX_ERROR_MESSAGE: RegExp = /(ERROR|WARNING)\s+(.+)\:(\d+)\:\s+(.*)/
const PARSER_MESSAGE_DELIMITER: string = "\t";
const REGEX_TOKEN_MGR_ERROR: RegExp = /.*?TokenMgrError\: Lexical error at line (\d+)/;
const REGEX_PARSE_EXCEPTION: RegExp = /.*?ParseException\:.*?at line (\d+)/;

/**
 * Execute KSP Compile program
 */
export class CompileExecutor implements vscode.Disposable {
    // HashMap holding a compiler instance for each document    
    private static pool: { [key: string]: CompileExecutor } = {};

    private _onError: ((txt: string) => void) | undefined;
    private _onException: ((e: Error) => void) | undefined;
    private _onStdout: ((txt: string) => void) | undefined;
    private _onStderr: ((txt: string) => void) | undefined;
    private _onEnd: (() => void) | undefined;
    private _onExit: ((exitCode: number) => void) | undefined;
    private running: boolean = false;
    private tempFile: any;
    private _diagnosticCollection: vscode.DiagnosticCollection = vscode.languages.createDiagnosticCollection();
    private diagnostics: vscode.Diagnostic[] = [];
    private _delayer: ThrottledDelayer<void> = new ThrottledDelayer<void>(0);

    private constructor() {
        this._delayer.defaultDelay = config.DEFAULT_VALIDATE_DELAY;
    }

    /**
     * Create the unique compiler instance per document
     */
    static getCompiler(document: vscode.TextDocument) {
        if (!document) {
            throw "textDocument is null";
        }
        let key = document.fileName;
        let compiler: CompileExecutor = CompileExecutor.pool[key];
        if (!compiler) {
            compiler = new CompileExecutor();
            CompileExecutor.pool[key] = compiler;
        }
        return compiler;
    }

    /**
     * Remove all callback events
     */
    protected unsetAllEvents(): void {
        this.OnEnd = () => undefined;
        this.OnError = () => undefined;
        this.OnException = () => undefined;
        this.OnExit = () => undefined;
        this.OnStderr = () => undefined;
        this.OnStdout = () => undefined;
    }

    /**
     * Clear diagnostics from problems view
     */
    protected clearDiagnostics(): void {
        this.DiagnosticCollection.clear();
    }

    /**
     * Must be called before the parser is running
     */
    public init(): CompileExecutor {
        this.unsetAllEvents();
        return this;
    }

    /**
     * Dispose resources
     */
    public dispose(): void {
        this.clearDiagnostics();
        this.unsetAllEvents();
    }

    /**
     * Dispose resources
     */
    public static dispose(document: vscode.TextDocument): void {
        const key = document.fileName;
        const compiler = this.pool[key];
        if (compiler) {
            compiler.dispose();
            delete this.pool[key];
        }
    }

    //--------------------------------------------------------------------------
    // Setter for callbacks
    //--------------------------------------------------------------------------
    set OnError(error: (txt: string) => void) {
        this._onError = error;
    }
    set OnException(exception: (e: Error) => void) {
        this._onException = exception;
    }
    set OnStdout(stdout: (txt: string) => void) {
        this._onStdout = stdout;
    }
    set OnStderr(stderr: (txt: string) => void) {
        this._onStderr = stderr;
    }
    set OnEnd(end: () => void) {
        this._onEnd = end;
    }
    set OnExit(exit: (exitCode: number) => void) {
        this._onExit = exit;
    }

    get DiagnosticCollection(): vscode.DiagnosticCollection {
        return this._diagnosticCollection;
    }

    get Delayer(): ThrottledDelayer<void> {
        return this._delayer;
    }

    /**
     * Parse stdout/stderr for generating diagnostics
     */
    private parseStdOut(lineText: string): void {
        let matches = lineText.match(REGEX_ERROR_MESSAGE);
        if (matches) {
            let level = matches[1];
            let line = Number.parseInt(matches[3]) - 1; // zero origin
            let message = "[KSP] " + matches[4];
            let range = new vscode.Range(line, 0, line, Number.MAX_VALUE);
            let diagnostic: vscode.Diagnostic = new vscode.Diagnostic(range, message);
            if (level === "ERROR") {
                diagnostic.severity = vscode.DiagnosticSeverity.Error;
            }
            else if (level === "WARNING") {
                diagnostic.severity = vscode.DiagnosticSeverity.Warning;
            }
            else if (level === "INFO" || level === "DEBUG") {
                diagnostic.severity = vscode.DiagnosticSeverity.Information;
            }
            else {
                diagnostic.severity = vscode.DiagnosticSeverity.Error;
            }
            this.diagnostics.push(diagnostic);
        }
    }

    /**
     * Parse stderr for generating diagnostics
     */
    private parseStdErr(lineText: string): void {
        let matches = lineText.match(REGEX_TOKEN_MGR_ERROR);
        if (!matches) {
            matches = lineText.match(REGEX_PARSE_EXCEPTION);
        }
        if (matches) {
            let message = "[KSP Compiler] FATAL: Check your script carefully again.";
            let line = Number.parseInt(matches[1]) - 1; // zero origin
            let diagnostic: vscode.Diagnostic = new vscode.Diagnostic(
                new vscode.Range(line, 0, line, Number.MAX_VALUE),
                message,
                vscode.DiagnosticSeverity.Error,
            );
            this.diagnostics.push(diagnostic);
        }
    }

    /**
     * Remove previous temp. file
     */
    private removeTempfile() {
        if (this.tempFile) {
            this.tempFile.removeCallback();
            this.tempFile = undefined;
        }
    }

    /**
     * Execute KSP syntax parser program (async)
     */
    private executeImpl(document: vscode.TextDocument, argBuilder: CompileBuilder, useDiagnostics: boolean = true): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            if (!ConfigurationManager.getConfig<boolean>(config.KEY_VALIDATE_ENABLE, config.DEFAULT_VALIDATE_ENABLE)) {
                vscode.window.showErrorMessage('KSP: Validate is disabled. See Preference of KSP');
                this.running = false;
                resolve();
                return;
            }
            this.diagnostics = [];
            // launch en-US mode
            // argBuilder.forceUseEn_US = true;
            //this.removeTempfile();
            //this.tempFile = tmp.fileSync();
            //fs.writeFileSync( this.tempFile.name, document.getText() );
            //argBuilder.inputFile = this.tempFile.name;
            let processFailed: boolean = false;
            try {
                let args: string[] = argBuilder.build();
                let python = ConfigurationManager.getConfig<string>(config.KEY_PYTHON_LOCATION, config.DEFAULT_PYTHON_LOCATION);
                let childProcess = child_process.spawn(python, args, undefined);
                childProcess.on('error', (error: Error) => {
                    this.removeTempfile();
                    this._diagnosticCollection.set(document.uri, undefined);
                    vscode.window.showErrorMessage('KSP: Command "python" not found');
                    if (this._onError) {
                        this._onError('KSP: Command "python" not found');
                    }
                    this.running = false;
                    resolve();
                });
                if (childProcess.pid) {
                    this.running = true;
                    processFailed = false;
                    // Handling stdout
                    childProcess.stdout.on('data', (data: Buffer) => {
                        if (useDiagnostics) {
                            data.toString().split(REGEX_PARSER_MESSAGE_NEWLINE).forEach(x => {
                                this.parseStdOut(x);
                            });
                        }
                        if (this._onStdout) {
                            this._onStdout(data.toString());
                        }
                        resolve();
                    });
                    // Handling stderr
                    childProcess.stderr.on('data', (data: Buffer) => {
                        if (useDiagnostics) {
                            data.toString().split(REGEX_PARSER_MESSAGE_NEWLINE).forEach(x => {
                                this.parseStdErr(x);
                            });
                        }
                        if (this._onStderr) {
                            this._onStderr(data.toString());
                        }
                        resolve();
                    });
                    // Process finished with exit code
                    childProcess.on('exit', (exitCode) => {
                        if (this._onExit) {
                            if (exitCode == null) {
                                exitCode = -1;
                                this._onExit(exitCode);
                            }
                        }
                        resolve();
                    });
                    // Process finished
                    childProcess.stdout.on('end', () => {
                        this.removeTempfile();
                        if (useDiagnostics) {
                            if (!document.isClosed) {
                                this.DiagnosticCollection.set(document.uri, this.diagnostics);
                            }
                            else {
                                this.clearDiagnostics();
                            }
                        }
                        if (this._onEnd) {
                            this._onEnd();
                        }
                        this.running = false;
                        resolve();
                    });
                }
                else {
                    if (this._onError) {
                        this._onError("child process is invalid");
                    }
                    this.running = false;
                    processFailed = true;
                }
            }
            catch (e) {
                this._diagnosticCollection.set(document.uri, undefined);
                if (this._onException) {
                    if (e instanceof Error) {
                        this._onException(e);
                    } else {
                        this._onException(new Error(String(e)));
                    }
                }
                this.running = false;
                reject(e)
            }
            finally {
                if (processFailed) {
                    this.removeTempfile();
                }
            }
        });
    }

    /**
     * Execute KSP syntax parser program
     */
    public execute(document: vscode.TextDocument, argBuilder: CompileBuilder, preSave: Boolean = true, useDiagnostics: boolean = true): void {
        if (document.languageId !== "ksp") {
            return;
        }
        if (this.running || document.isClosed) {
            return;
        }
        // Pre-Save.
        // TODO Conflict: Save Document Event handling@KSPValidationProvider
        // if( preSave && ( !document.isUntitled && document.isDirty ) )
        // {
        //     document.save().then((fulfilled)=>{
        //         if( fulfilled )
        //         {
        //             this._delayer.trigger( () => this.executeImpl( document, argBuilder, useDiagnostics ) );
        //         }
        //     });
        //     return;
        // }
        this._delayer.trigger(() => this.executeImpl(document, argBuilder, useDiagnostics));
    }
}
