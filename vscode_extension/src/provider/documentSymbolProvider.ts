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
import { SymbolUtil, SymbolInformation, SymbolType, Symbol } from '../util/symbolUtil';

export class DocumentSymbolProvider implements vscode.DocumentSymbolProvider {
    constructor() { }

    public provideDocumentSymbols(
        document: vscode.TextDocument,
        token: vscode.CancellationToken
    ): Thenable<vscode.DocumentSymbol[]> {
        let result: vscode.DocumentSymbol[] = [];
        const symbols: SymbolInformation[] = SymbolUtil.collect(document);
        let createSymbol = function (v: SymbolInformation, kind: vscode.SymbolKind) {
            let range: vscode.Range = v.location.range;
            let selectionRange: vscode.Range = v.location.range;
            if (v.range && v.selectionRange) {
                range = v.range;
                selectionRange = v.selectionRange;
            }
            return new vscode.DocumentSymbol(v.name,
                v.Symbol.description,
                kind,
                range,
                selectionRange)
        }
        for (const v of symbols) {
            const ksp = v.Symbol;
            //------------------------------------------------------------------
            // Callback
            //------------------------------------------------------------------
            if (ksp.symbolType == SymbolType.CALLBACK) {
                //v.name = "on " + v.name;
                if (ksp.isUI) {
                    v.name += " : " + ksp.uiVariableName + " (" + ksp.uiVariableType + ")";
                }
                result.push(createSymbol(v, vscode.SymbolKind.Event));
            }
            //------------------------------------------------------------------
            // Variable
            //------------------------------------------------------------------
            if (ksp.symbolType >= SymbolType.VARIABLE_TYPE_BEGIN && ksp.symbolType <= SymbolType.VARIABLE_TYPE_END) {
                let sym = createSymbol(v, vscode.SymbolKind.Variable);
                sym.name = Symbol.variableType2Char(ksp.symbolType) + sym.name;
                if (ksp.isPolyphonic) {
                    sym.name += ": " + ksp.variableTypeName + ", Polyphonic";
                }
                else if (ksp.isUI) {
                    sym.name += ": " + ksp.variableTypeName;
                }
                else {
                    sym.name += ": " + ksp.variableTypeName;
                }
                if (ksp.isConst) {
                    sym.kind = vscode.SymbolKind.Constant;
                }
                else if (Symbol.isArrayVariable(ksp.symbolType)) {
                    sym.kind = vscode.SymbolKind.Array;
                }
                result.push(sym);
            }
            //------------------------------------------------------------------
            // User Fumction
            //------------------------------------------------------------------
            if (ksp.symbolType == SymbolType.USER_FUNCTION) {
                //v.name = "function " + v.name;
                result.push(createSymbol(v, vscode.SymbolKind.Function));
            }
        }
        return Promise.resolve(result);
    }
}
