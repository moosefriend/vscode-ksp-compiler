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
// Implemented based on Part of PHP Signature Help Provider implementation. (signatureHelpProvider.ts)
import vscode = require('vscode');
import * as Commands from '../generated/commandCompletion';
import { CompletionRecord } from '../config/completionRecord';

const _Newline = '\n'.charCodeAt(0);
const _TAB = '\t'.charCodeAt(0);
const _Whitespace = ' '.charCodeAt(0);
const _LSquareBracket = '['.charCodeAt(0);
const _RSquareBracket = ']'.charCodeAt(0);
const _LCurlyBracket = '{'.charCodeAt(0);
const _RCurlyBracket = '}'.charCodeAt(0);
const _LRoundBracket = '('.charCodeAt(0);
const _RRoundBracket = ')'.charCodeAt(0);
const _Comma = ','.charCodeAt(0);
const _SingleQuote = '\''.charCodeAt(0);
const _DoubleQuote = '"'.charCodeAt(0);
const _Underscore = '_'.charCodeAt(0);
const _a = 'a'.charCodeAt(0);
const _z = 'z'.charCodeAt(0);
const _A = 'A'.charCodeAt(0);
const _Z = 'Z'.charCodeAt(0);
const _0 = '0'.charCodeAt(0);
const _9 = '9'.charCodeAt(0);
const BeginOfFile = 0;

export class BackwardIterator {
    lineNumber: number;
    offset: number;
    line: string;
    textDocument: vscode.TextDocument;

    /**
     * Creates a backward iterator to check previous characters.
     * @param textDocument Current text document
     * @param offset Character offset in the line below
     * @param lineNumber Line number in the text document
     */
    constructor(textDocument: vscode.TextDocument, offset: number, lineNumber: number) {
        this.lineNumber = lineNumber;
        this.offset = offset;
        this.line = textDocument.lineAt(this.lineNumber).text;
        this.textDocument = textDocument;
    }

    /**
     * @returns True if there is still a current or previous lines
     */
    public hasPrevChar() {
        return this.lineNumber >= 0;
    }

    /**
     * @returns Previous character of the current line. If it is at the beginning of the line it returns the last character for the previous line.
     */
    public prevChar() {
        if (this.offset < 0) {
            if (this.lineNumber > 0) {
                this.lineNumber--;
                this.line = this.textDocument.lineAt(this.lineNumber).text;
                this.offset = this.line.length - 1;
                return _Newline;
            }
            this.lineNumber = -1;
            return BeginOfFile;
        }
        let ch = this.line.charCodeAt(this.offset);
        this.offset--;
        return ch;
    }
}

export class SignatureHelpProvider implements vscode.SignatureHelpProvider {
    constructor() { }

    /**
     * Implementation of function signature behaviour
     */
    public provideSignatureHelp(textDocument: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken) {
        let iterator = new BackwardIterator(textDocument, position.character - 1, position.line);
        // Check how many parameters are currently entered by the user
        let paramCount = this.countParameters(iterator);
        // If no open round bracket is found (as beginning of the parameter list) then return null 
        if (paramCount < 0) {
            return null;
        }
        // Get the function name
        let identifier = this.getIdentifier(iterator);
        if (!identifier) {
            return null;
        }
        // Check if the function name matches one of the commands
        let entry: CompletionRecord | undefined = Commands.CompletionList.get(identifier);
        if (!entry || !entry.signature) {
            return null;
        }
        let paramsString = entry.signature.substring(0, entry.signature.lastIndexOf(')') + 1);
        let signatureInfo = new vscode.SignatureInformation(identifier + paramsString, entry.description);
        let re = /\w*\s*[\w_\.]+|void/g;
        let match = null;
        while ((match = re.exec(paramsString)) !== null) {
            signatureInfo.parameters.push({ label: match[0], documentation: '' });
        }
        let ret = new vscode.SignatureHelp();
        ret.signatures.push(signatureInfo);
        ret.activeSignature = 0;
        ret.activeParameter = Math.min(paramCount, signatureInfo.parameters.length - 1);
        return Promise.resolve(ret);
    }

    /**
     * Get the number of currently entered parameters of a function
     * @param iterator Backward iterator which gets the previous character
     * @returns Number of parameters or -1 if there are no round brackets
     */
    private countParameters(iterator: BackwardIterator): number {
        let roundBracketNesting: number = 0;
        let squareBracketNesting: number = 0;
        let curlyBracketNesting: number = 0;
        let paramCount: number = 0;
        while (iterator.hasPrevChar()) {
            let ch = iterator.prevChar();
            switch (ch) {
                case _LRoundBracket:
                    roundBracketNesting--;
                    if (roundBracketNesting < 0) {
                        return paramCount;
                    }
                    break;
                case _RRoundBracket:
                    roundBracketNesting++;
                    break;
                case _LCurlyBracket:
                    curlyBracketNesting--;
                    break;
                case _RCurlyBracket:
                    curlyBracketNesting++;
                    break;
                case _LSquareBracket:
                    squareBracketNesting--;
                    break;
                case _RSquareBracket:
                    squareBracketNesting++;
                    break;
                case _DoubleQuote:
                case _SingleQuote:
                    while (iterator.hasPrevChar() && ch !== iterator.prevChar()) { }
                    break;
                case _Comma:
                    if (!roundBracketNesting && !squareBracketNesting && !curlyBracketNesting) {
                        paramCount++;
                    }
                    break;
            }
        }
        return -1;
    }

    /**
     * @param ch Character to check
     * @returns True if the character is an identifier character, false otherwise
     */
    private static isIdentifierChar(ch: number) {
        if (ch === _Underscore ||
            ch >= _a && ch <= _z ||
            ch >= _A && ch <= _Z ||
            ch >= _0 && ch <= _9 ||
            ch >= 0x80 && ch <= 0xFFFF) {
            return true;
        }
        return false;
    }

    /**
     * Get identifier before the current position
     * @param iterator Backward iterator to get the previous character
     * @returns Found identifier or an empty string
     */
    private getIdentifier(iterator: BackwardIterator): string {
        let identifierStarted: boolean = false;
        let identifier: string = '';
        while (iterator.hasPrevChar()) {
            let ch = iterator.prevChar();
            if (!identifierStarted && (ch === _Whitespace || ch === _TAB || ch === _Newline)) {
                continue;
            }
            if (SignatureHelpProvider.isIdentifierChar(ch)) {
                identifierStarted = true;
                identifier = String.fromCharCode(ch) + identifier;
            }
            else if (identifierStarted) {
                return identifier;
            }
        }
        return identifier;
    }
}
