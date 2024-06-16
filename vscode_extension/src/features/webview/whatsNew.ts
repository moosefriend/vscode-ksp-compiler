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
import * as path from 'path';
import * as fs from 'fs';
import * as tmp from 'tmp';
import * as constant from '../constants';

export function show() {
    const WEBVIEW_ROOT = path.join(
        constant.EXTENSION_DIR,
        "resources",
        "webview"
    );

    //let resourceRoot: vscode.Uri[] = [ vscode.Uri.file( WEBVIEW_ROOT ).with( {scheme: "vscode-resource"} ) ];
    let panel: vscode.WebviewPanel = vscode.window.createWebviewPanel(
        "whatsnewksp",
        "KSP - What's new",
        vscode.ViewColumn.One,
        {
            enableScripts: false,
            //localResourceRoots: resourceRoot
        }
    );

    panel.webview.html = fs.readFileSync(path.join(
        WEBVIEW_ROOT,
        "whatsnew.html")
    ).toString();
}
