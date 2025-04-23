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
// Implemented based on Part of PHP HOver Provider implementation. (hoverProvider.ts)

'use strict';

import vscode = require('vscode');

var builtinVariables = require('./generated/variableCompletion');
var commands = require('./generated/commandCompletion');

export class HoverProvider implements vscode.HoverProvider {
    /**
     * Ctor.
     */
    constructor() { }

    /**
     * Implementation of Hover behaviour
     */
    public provideHover(textDocument: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken): vscode.Hover | null {
        let wordRange: vscode.Range | undefined = textDocument.getWordRangeAtPosition(position);
        if (!wordRange) {
            return null;
        }

        let name: string = textDocument.getText(wordRange);
        let entry: any = commands.CompletionList[name] || builtinVariables.CompletionList[name];

        if (entry && entry.description) {
            let signature = entry.signature || '';
            let contents = [entry.description, { language: 'ksp', value: signature }];
            return new vscode.Hover(contents, wordRange);
        }
        return null;
    }
}
