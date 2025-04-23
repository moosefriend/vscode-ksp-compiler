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
import * as vscode from 'vscode';
import * as path from 'path';

export const EXTENSION_ID: string = 'source.ksp';
export const LANG_ID: string = 'ksp';
export const EXTENSION_DIR = vscode.extensions.getExtension(EXTENSION_ID).extensionPath;
export const RES_BASEDIR = path.join(EXTENSION_DIR, 'etc', 'images', 'icon');
