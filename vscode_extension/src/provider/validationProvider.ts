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
// Implemented based on Part of PHP Validation Provider implementation. (validationProvider.ts)
import * as vscode from 'vscode';
import { ThrottledDelayer } from '../lib/async';
import * as config from '../config/configurationConstants';
import { ConfigurationManager } from '../config/configurationManager';
import { CompileExecutor } from '../compiler/compileExecutor';
import { CompileBuilder } from '../compiler/compileBuilder';
import { Channel } from '../compiler/commandSetup';
import * as tmp from 'tmp';

export class ValidationProvider {
    private validationEnabled: boolean = ConfigurationManager.getConfig<boolean>(config.KEY_VALIDATE_ENABLE);
    private realtimeValidationEnabled: boolean = true;
    private realtimeValidationDelay: number = ConfigurationManager.getConfig<number>(config.KEY_VALIDATE_DELAY);
    private executable: string = ConfigurationManager.getConfig<string>(config.KEY_PYTHON_LOCATION);
    private pauseValidation: boolean = false;
    private realtimeTrigger: boolean = false;
    private onSaveListener: vscode.Disposable | undefined;
    private onChangedListener: vscode.Disposable | undefined;

    constructor(private workspaceStore: vscode.Memento) { }

    /**
     * Provider activated
     */
    public activate(context: vscode.ExtensionContext) {
        const subscriptions: vscode.Disposable[] = context.subscriptions;
        this.initConfiguration();
        this.loadConfiguration();
        vscode.workspace.onDidChangeConfiguration(this.loadConfiguration, this, subscriptions);
        vscode.workspace.onDidOpenTextDocument((document) => {
            this.doValidate(document);
        }, null, subscriptions);
        vscode.workspace.onDidCloseTextDocument((textDocument) => {
            CompileExecutor.dispose(textDocument);
        }, null, subscriptions);
    }

    /**
     * Safety dispose
     */
    public doDispose(p?: vscode.Disposable) {
        if (p) p.dispose();
    }

    /**
     * Initialize configuration.
     * When this is the first time to activate this extention, store default values.
     */
    private initConfiguration(): void {
        let section: vscode.WorkspaceConfiguration = vscode.workspace.getConfiguration(config.CONFIG_SECTION_NAME);
        if (section) {
            let initConfig = function <T>(key: string) {
                if (!section.has(key)) {
                    let inspect = section.inspect<T>(key);
                    if (inspect && inspect.defaultValue !== undefined && inspect.defaultValue !== null) {
                        section.update(key, inspect.defaultValue as T, true);
                    }
                }
            };
            initConfig<boolean>(config.KEY_VALIDATE_ENABLE);
            initConfig<number>(config.KEY_VALIDATE_DELAY);
        }
    }

    /**
     * Load configuration for validation
     */
    private loadConfiguration(): void {
        let section: vscode.WorkspaceConfiguration = vscode.workspace.getConfiguration(config.CONFIG_SECTION_NAME);
        let oldExecutable = this.executable;
        if (section) {
            // Get configurations
            this.validationEnabled = ConfigurationManager.getConfig<boolean>(config.KEY_VALIDATE_ENABLE);
            this.executable = ConfigurationManager.getConfig<string>(config.KEY_PYTHON_LOCATION);
            ConfigurationManager.getConfigComplex<number>(config.KEY_VALIDATE_DELAY, (value, user) => {
                if (value == 0) {
                    this.realtimeValidationEnabled = false;
                }
                else {
                    this.realtimeValidationEnabled = true;
                    if (value < 16) {
                        let inspect = section.inspect<number>(config.KEY_VALIDATE_DELAY);
                        let def = (inspect && inspect.defaultValue !== undefined && inspect.defaultValue !== null) ? inspect.defaultValue as number : 500;
                        this.realtimeValidationDelay = def;
                        section.update(config.KEY_VALIDATE_DELAY, def, true);
                        vscode.window.showWarningMessage("KSP Configuration: " + config.KEY_VALIDATE_DELAY + ": too short or negative. Reset default time.");
                    }
                    else {
                        this.realtimeValidationDelay = value;
                    }
                }
            });
            // ~Get configurations
            if (this.pauseValidation) {
                this.pauseValidation = oldExecutable === this.executable;
            }
            this.doDispose(this.onChangedListener);
            this.doDispose(this.onSaveListener);
            if (!this.validationEnabled) {
                return;
            }
            this.onSaveListener = vscode.workspace.onDidSaveTextDocument((e) => {
                this.realtimeTrigger = false;
                this.doValidate(e);
            }, this);
            this.onChangedListener = vscode.workspace.onDidChangeTextDocument((e) => {
                if (this.realtimeValidationEnabled) {
                    this.realtimeTrigger = true;
                    this.doValidate(e.document);
                }
            });
            if (this.validationEnabled) {
                let documents: readonly vscode.TextDocument[] = vscode.workspace.textDocuments;
                if (documents) {
                    documents.forEach((doc: vscode.TextDocument) => {
                        this.doValidate(doc);
                    });
                }
            }
        }
    }

    /**
     * Execute syntax parser program
     */
    private doValidate(textDocument: vscode.TextDocument): void {
        let compiler: CompileExecutor = CompileExecutor.getCompiler(textDocument);
        // If there is a programatic save command initiated, then avoid double validation
        if (!this.validationEnabled || compiler.isProgrammaticSave) {
            return;
        }
        let src: string = textDocument.fileName;
        let tmpFile = tmp.fileSync();
        let argBuilder: CompileBuilder = new CompileBuilder(src, tmpFile.name);
        let delayer: ThrottledDelayer<void> = compiler.Delayer;
        let delay = this.realtimeTrigger ? this.realtimeValidationDelay : 0;
        if (this.realtimeValidationEnabled) {
            delayer.defaultDelay = delay;
        }
        compiler.init();
        compiler.OnError = (text: string) => {
            if (this.pauseValidation) {
                return;
            }
            this.pauseValidation = true;
        };
        compiler.execute(textDocument, argBuilder);
    }
}
