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
import * as fs from 'fs';
import * as path from 'path';
import * as tmp from 'tmp';
import { CompileBuilder } from '../compiler/compileBuilder';
import { CompileExecutor } from '../compiler/compileExecutor';

export async function doCompile(context: vscode.ExtensionContext) {
    let editor: vscode.TextEditor | undefined = vscode.window.activeTextEditor;
    let textDocument: vscode.TextDocument;
    let baseName: string;
    let scriptFilePath: string;
    let tmpFile: tmp.FileResult;
    const MESSAGE_PREFIX: string = "KSP";
    const MESSAGE_FAILED: string = "Failed";
    const MESSAGE_CLIPBOARD: string = "Script has been copied to clipboard";

    //--------------------------------------------------------------------------
    // Preverify
    //--------------------------------------------------------------------------
    // Any files not opened
    if (!editor) {
        vscode.window.showErrorMessage("Editor not opened");
        return;
    }
    textDocument = editor.document;
    if (textDocument.languageId !== "ksp") {
        vscode.window.showErrorMessage(`${MESSAGE_PREFIX}: Language mode is not 'ksp'`);
        return;
    }
    scriptFilePath = textDocument.fileName;
    baseName = path.basename(textDocument.fileName);

    //--------------------------------------------------------------------------
    // Run compiler
    //--------------------------------------------------------------------------
    function runCompiler(callback?: (exitCode: number) => void) {
        tmpFile = tmp.fileSync();
        let argBuilder: CompileBuilder = new CompileBuilder(scriptFilePath, tmpFile.name);
        let compiler: CompileExecutor = CompileExecutor.getCompiler(textDocument).init();
        compiler.OnExit = (exitCode: number) => {
            if (exitCode != 0) {
                vscode.window.showErrorMessage(`${MESSAGE_PREFIX}: ${MESSAGE_FAILED}. Please check your script: ${baseName}`);
            }
            else {
                vscode.window.showInformationMessage(`${MESSAGE_PREFIX}: ${MESSAGE_CLIPBOARD}`);
            }
            if (callback) {
                callback(exitCode);
            }
        };
        compiler.OnException = (e: Error) => {
            vscode.window.showErrorMessage(`${MESSAGE_PREFIX}: ${MESSAGE_FAILED}: ${baseName}`);
        };
        compiler.execute(textDocument, argBuilder);
    };

    // Output to Clipboard
    // Dynamically import clipboardy
    const clipboard = await import('clipboardy');
    {
        runCompiler((exitCode) => {
            if (exitCode == 0) {
                let txt: string = fs.readFileSync(tmpFile.name).toString();
                clipboard.default.writeSync(txt);
            }
            try {
                tmpFile.removeCallback();
            }
            catch (e) {
                // Ignore exceptions
            }
        });
    }
}
