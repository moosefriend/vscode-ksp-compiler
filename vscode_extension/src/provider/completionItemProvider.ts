/**
 * This file is part of the vscode-ksp-compiler distribution
 * (https://github.com/moosefriend/vscode-ksp-compiler).
 *
 * Copyright (c) 2025 MooseFriend (https://github.com/moosefriend)
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
// Implemented based on Part of PHP Completion ItemProvider implementation. (completionItemProvider.ts)

import vscode = require('vscode');
import * as Variables from "../generated/variableCompletion";
import * as Commands from "../generated/commandCompletion";
import { CompletionRecord } from '../config/completionRecord';
export const VARIABLE_PREFIX_LIST: string[] = ['$', '%', '~', '?', '@', '!'];
export const VARIABLE_REGEX: RegExp = /([\$%~\?@!][0-9a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)/g;
export const FUNCTION_REGEX: RegExp = /function\s+([0-9a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)\s*/g

export class CompletionItemProvider implements vscode.CompletionItemProvider {
    constructor() { }

    /**
     * Implementation of completion behaviour
     */
    public provideCompletionItems(textDocument: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken): Promise<any[]> {
        let result: vscode.CompletionItem[] = [];
        let range = textDocument.getWordRangeAtPosition(position);
        let prefix = range ? textDocument.getText(range) : '';
        let text = textDocument.getText();
        if (!range) {
            range = new vscode.Range(position, position);
        }
        let added: Record<string, boolean> = {};
        //----------------------------------------------------------------------
        // Proposal component
        //----------------------------------------------------------------------
        let createNewProposal = function (kind: vscode.CompletionItemKind, name: string, entry: CompletionRecord | null) {
            let proposal = new vscode.CompletionItem(name);
            proposal.kind = kind;
            if (entry) {
                if (entry.description) {
                    proposal.documentation = entry.description;
                }
                if (entry.signature) {
                    proposal.detail = entry.signature;
                }
                if (entry.snippet) {
                    proposal.insertText = new vscode.SnippetString(entry.snippet);
                }
            }
            return proposal;
        };
        //----------------------------------------------------------------------
        // Matcher: The prefix is the text entered by the user
        // The matcher checks if the name starts with the prefix.
        //----------------------------------------------------------------------
        let matches = function (name: string) {
            return prefix.length === 0 ||
                name.length >= prefix.length &&
                name.substring(0, prefix.length) === prefix;
        };
        //----------------------------------------------------------------------
        // Check if the prefix matches some built-in variables
        //----------------------------------------------------------------------
        Variables.CompletionList.forEach(function (entry: CompletionRecord, name: string) {
            if (matches(name)) {
                added[name] = true;
                result.push(createNewProposal(vscode.CompletionItemKind.Variable, name, entry));
            }
        });
        //----------------------------------------------------------------------
        // Check if the prefix mathes some commands
        //----------------------------------------------------------------------
        Commands.CompletionList.forEach(function (entry: CompletionRecord, name: string) {
            if (matches(name)) {
                added[name] = true;
                result.push(createNewProposal(vscode.CompletionItemKind.Function, name, entry));
            }
        });
        //----------------------------------------------------------------------
        // Check if the prefix mathces some user variables in the same file
        //----------------------------------------------------------------------
        {
            let prefixMatched = false;
            VARIABLE_PREFIX_LIST.forEach(function (element) {
                if (prefixMatched) return;
                if (prefix[0] === element) {
                    prefixMatched = true;
                }
            });
            if (prefixMatched) {
                let variableMatch = VARIABLE_REGEX;
                let match = null;
                while (match = variableMatch.exec(text)) {
                    let word = match[0];
                    if (!added[word]) {
                        added[word] = true;
                        result.push(createNewProposal(vscode.CompletionItemKind.Variable, word, null));
                    }
                }
            }
        }
        //----------------------------------------------------------------------
        // Check if the prefix mathces some user functions in the same file
        //----------------------------------------------------------------------
        {
            let functionMatch = FUNCTION_REGEX;
            let match = null;
            while (match = functionMatch.exec(text)) {
                let word = match[1];
                if (!added[word]) {
                    added[word] = true;
                    result.push(createNewProposal(vscode.CompletionItemKind.Function, word, null));
                }
            }
        }
        return Promise.resolve(result);
    }

    /**
     * Given a completion item fill in more data
     */
    public resolveCompletionItem?(item: vscode.CompletionItem, token: vscode.CancellationToken): vscode.ProviderResult<vscode.CompletionItem> {
        // No additional information
        return item;
    }
}
