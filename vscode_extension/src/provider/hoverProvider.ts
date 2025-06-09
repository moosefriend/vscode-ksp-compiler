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
import vscode = require('vscode');
import VariableCompletions = require('../generated/variableCompletion');
import CommandCompletions = require('../generated/commandCompletion');

export class HoverProvider implements vscode.HoverProvider {
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
        let entry: any = CommandCompletions.CompletionList.get(name) || VariableCompletions.CompletionList.get(name);
        console.log('HoverProvider called for:', name, 'Entry:', entry);
        if (entry) {
            const description = entry.get('description');
            const signature = entry.get('signature') || '';
            if (description) {
                let contents = [description, { language: 'ksp', value: signature }];
                return new vscode.Hover(contents, wordRange);
            }
        }
        return null;
    }
}
