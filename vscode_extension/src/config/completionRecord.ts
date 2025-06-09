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
export class CompletionRecord {
    public readonly name: string;
    public readonly description: string;
    public readonly signature: string;
    public readonly snippet: string;
    
    public constructor(name: string, description: string, signature: string, snippet: string) {
        this.name = name;
        this.description = description;
        this.signature = signature;
        this.snippet = snippet;
    }
}