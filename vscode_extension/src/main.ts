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
import * as Constants from './config/constants';
import { CompletionItemProvider } from './provider/completionItemProvider';
import { HoverProvider } from './provider/hoverProvider';
import { SignatureHelpProvider } from './provider/signatureHelpProvider';
import { DocumentSymbolProvider } from './provider/documentSymbolProvider';
import { DefinitionProvider } from './provider/definitionProvider';
import { ReferenceProvider } from './provider/referenceProvider';
import { ValidationProvider } from './provider/validationProvider';
import { RenameProvider } from './provider/renameProvider';
import CommandSetup = require('./compiler/commandSetup');

export function activate(context: vscode.ExtensionContext): any {
    // Providers
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(
            Constants.LANG_ID, new CompletionItemProvider(), '$', '%', '~', '?', '@', '!')
    );
    context.subscriptions.push(
        vscode.languages.registerHoverProvider(Constants.LANG_ID, new HoverProvider())
    );
    context.subscriptions.push(
        vscode.languages.registerSignatureHelpProvider(Constants.LANG_ID, new SignatureHelpProvider(), '(', ',')
    );
    context.subscriptions.push(
        vscode.languages.registerDocumentSymbolProvider(Constants.LANG_ID, new DocumentSymbolProvider())
    );
    context.subscriptions.push(
        vscode.languages.registerDefinitionProvider(Constants.LANG_ID, new DefinitionProvider())
    );
    context.subscriptions.push(
        vscode.languages.registerReferenceProvider(Constants.LANG_ID, new ReferenceProvider())
    );
    context.subscriptions.push(
        vscode.languages.registerRenameProvider(Constants.LANG_ID, new RenameProvider())
    );
    // Commands
    CommandSetup.setupCommands(context);
    // Language Configuration
    vscode.languages.setLanguageConfiguration(Constants.LANG_ID,
        { wordPattern: /(-?\d*\.\d\w*)|([^\-\`\#\^\&\*\(\)\=\+\[\{\]\}\\\|\;\:\'\"\,\.\<\>\/\?\s]+)/g }
    );
    // Other setup
    const validator = new ValidationProvider(context.workspaceState);
    validator.activate(context);
}
