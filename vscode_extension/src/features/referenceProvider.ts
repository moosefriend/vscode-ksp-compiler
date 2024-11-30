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
import CommandNameList = require('./generated/commandNames');
import VariableNameList = require('./generated/variableNames');

import { SymbolUtil } from './symbolUtil';
import { SymbolType } from './symbolUtil';
import { Symbol } from './symbolUtil';
import { SymbolInformation } from './symbolUtil';

export class ReferenceProvider implements vscode.ReferenceProvider {
    constructor() {
    }

    public provideReferences(
        document: vscode.TextDocument,
        position: vscode.Position,
        context: vscode.ReferenceContext,
        token: vscode.CancellationToken): Thenable<Array<vscode.Location>> | null {
        let symbols: SymbolInformation[] = SymbolUtil.collect(document);
        if (!symbols) {
            return null;
        }
        let result: vscode.Location[] = [];
        let symbol: string = SymbolUtil.parseSymbolAt(document, position);
        let lineCount: number = document.lineCount;
        for (let i = 0; i < lineCount; i++) {
            let text: string = document.lineAt(i).text.trim();
            let words: string[] = text.split(/[\s|,|\[|\]|\(|\)]+/);

            // Builtin-Commands?
            words.forEach(w => {
                let found: boolean = false;
                if (w == symbol) {
                    CommandNameList.CommandNames.forEach(cmd => {
                        if (cmd == symbol) {
                            result.push(new vscode.Location(
                                document.uri,
                                new vscode.Position(i, 0)
                            ));
                            found = true;
                            return;
                        }
                    });
                }
                if (found) {
                    return;
                }
            });
            // Builtin-Variables?
            words.forEach(w => {
                let found: boolean = false;
                if (w == symbol) {
                    VariableNameList.BuiltinVariableNames.forEach(v => {
                        if (v == symbol) {
                            result.push(new vscode.Location(
                                document.uri,
                                new vscode.Position(i, 0)
                            ));
                            found = true;
                            return;
                        }
                    });
                }
                if (found) {
                    return;
                }
            });
            // User definition
            symbols.forEach(x => {
                let sym: Symbol = x.Symbol;
                let symName: string = sym.name;

                // User Function?
                if (symName == symbol) {
                    words.forEach(w => {
                        if (w == symbol) {
                            result.push(new vscode.Location(
                                document.uri,
                                new vscode.Position(i, 0)
                            ));
                            return;
                        }
                    });
                }
                // Variable?
                else if (x.Symbol.toVariableNameFormat() == symbol) {
                    words.forEach(w => {
                        if (w == symbol) {
                            result.push(new vscode.Location(
                                document.uri,
                                new vscode.Position(i, 0)
                            ));
                            return;
                        }
                    });
                }
            });
        }
        return Promise.resolve(result);
    }
}
