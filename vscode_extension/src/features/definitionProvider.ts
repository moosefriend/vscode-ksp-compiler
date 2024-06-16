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

import { SymbolUtil } from './symbolUtil';
import { SymbolType } from './symbolUtil';
import { Symbol } from './symbolUtil';
import { SymbolInformation } from './symbolUtil';

export class DefinitionProvider implements vscode.DefinitionProvider {
    constructor() {
    }

    public provideDefinition(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken): Thenable<vscode.Location[]> | null {
        let symbols: SymbolInformation[] = SymbolUtil.collect(document);
        if (!symbols) {
            return null;
        }
        let result: vscode.Location[] = [];
        let textLine: vscode.TextLine = document.lineAt(position.line);
        let symbol: string = SymbolUtil.parseSymbolAt(document, position);

        symbols.forEach(x => {
            let sym: Symbol = x.Symbol;
            let symName: string = sym.name;
            let declaredLine: boolean = sym.lineNumber == textLine.lineNumber;

            // User Function?
            if (!declaredLine && symName == symbol) {
                result.push(x.location);
            }
            // Variable?
            else if (x.Symbol.toVariableNameFormat() == symbol) {
                if (!declaredLine) {
                    result.push(x.location);
                }

                // For UI Callback?
                if (x.Symbol.isUI) {
                    symbols.forEach(y => {
                        if (y.Symbol.isUI && y.Symbol.symbolType == SymbolType.CALLBACK &&
                            y.Symbol.toVariableNameFormat(true) == symbol) {
                            result.push(y.location);
                        }
                    });
                }
            }
        });
        return Promise.resolve(result);
    }
}
