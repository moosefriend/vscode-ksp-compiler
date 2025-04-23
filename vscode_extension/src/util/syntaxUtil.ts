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

export const BASIC_KEYWORDS: string[] = [
    "on",
    "end",
    "function",
    "declare",
    "const",
    "polyphonic",
    "if",
    "else",
    "select",
    "case",
    "to",
    "while",
    "mod",
    "and",
    "or",
    "not",
    ".and.",
    ".or.",
    ".not.",
    "call",
]

export const REGEXP_DECIMAL: RegExp = /\b(0|[1-9][0-9]*)/;
export const REGEXP_HEXADECIMAL: RegExp = /\b9[0-9a-fA-F]h/;
export const REGEXP_REAL: RegExp = /\b(0|[1-9][0-9]*)\.[0-9]*/;
export const REGEXP_STRING: RegExp = /"[^"]+"/;

export default class KSPSyntaxUtil {
    private constructor() { }

    static matchKeyword(text: string): boolean {
        return BASIC_KEYWORDS.indexOf(text) != -1;
    }

    static matchDecimal(text: string): boolean {
        return text.match(REGEXP_DECIMAL) != null;
    }

    static matchHexadecimal(text: string): boolean {
        return text.match(REGEXP_HEXADECIMAL) != null;
    }

    static matchReal(text: string): boolean {
        return text.match(REGEXP_REAL) != null;
    }

    static matchString(text: string): boolean {
        return text.match(REGEXP_STRING) != null;
    }

    static matchLiteral(text: string): boolean {
        return KSPSyntaxUtil.matchDecimal(text) ||
            KSPSyntaxUtil.matchHexadecimal(text) ||
            KSPSyntaxUtil.matchReal(text) ||
            KSPSyntaxUtil.matchString(text);
    }

}
