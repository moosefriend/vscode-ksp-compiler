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
import CompileCommand = require('./compileCommand');
//import WhatsNew = require( '../webview/whatsNew' );

/**
 * Define the output window for the KSP Compiler
 */
export let outputChannel: vscode.OutputChannel;

/**
 * Register this extension's commands
 */
export function setupCommands(context: vscode.ExtensionContext) {
    outputChannel = vscode.window.createOutputChannel('KSP Compiler');
    context.subscriptions.push(
        vscode.commands.registerCommand('ksp.compile', CompileCommand.doCompile)
    );

    // context.subscriptions.push(
    //     vscode.commands.registerCommand('ksp.webview.whatsnew', WhatsNew.show )
    // );
}
