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
import {
    Range,
    TextDocument,
    Position,
    CancellationToken,
    ProviderResult,
    WorkspaceEdit
} from 'vscode';

import KSPExtensionConstants = require('../config/constants');
import {
    SymbolUtil,
    SymbolType,
    Symbol,
    SymbolInformation
} from '../util/symbolUtil';

import SyntaxUtil from '../util/syntaxUtil';

export class RenameProvider implements vscode.RenameProvider {
    public provideRenameEdits(document: TextDocument,
        position: Position,
        newName: string,
        token: CancellationToken): ProviderResult<WorkspaceEdit> {
        return new Promise<vscode.WorkspaceEdit>((ressolve, reject) => {

            if (!newName) {
                reject();
            }

            const result: WorkspaceEdit = new WorkspaceEdit();
            const symbols: SymbolInformation[] = SymbolUtil.collect(document);
            const org: string = SymbolUtil.parseSymbolAt(document, position);
            let renamed: boolean = false;
            let regex: RegExp | undefined = undefined;

            if (Symbol.isVariable(org)) {
                regex = new RegExp("\\" + org, 'g');
            }
            else if (!SyntaxUtil.matchKeyword(org) && !SyntaxUtil.matchLiteral(org)) {
                regex = new RegExp(org, "g");
            }

            // replace
            if (regex) {
                for (let i = 0; i < document.lineCount; i++) {
                    let lineText = document.lineAt(i).text;
                    if (lineText.match(regex)) {
                        let orgLength = lineText.length;
                        lineText = lineText.replace(regex, newName);
                        result.replace(document.uri, new Range(i, 0, i, orgLength), lineText);
                    }
                }
                renamed = true;
            }

            if (renamed) {
                ressolve(result);
            }
            else {
                reject();
            }
        });
    }
}
