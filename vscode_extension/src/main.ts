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
'use strict';

import vscode  = require('vscode');
import * as Constants from './features/constants';
import {CompletionItemProvider} from './features/completionItemProvider';
import {HoverProvider} from './features/hoverProvider';
import {SignatureHelpProvider} from './features/signatureHelpProvider';
import {DocumentSymbolProvider} from './features/documentSymbolProvider';
import {DefinitionProvider} from './features/definitionProvider';
import {ReferenceProvider} from './features/referenceProvider';
import {ValidationProvider} from './features/validationProvider';
import {RenameProvider} from './features/renameProvider';
import CommandSetup = require('./features/commands/commandSetup');

export function activate(context: vscode.ExtensionContext): any
{
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
        {wordPattern: /(-?\d*\.\d\w*)|([^\-\`\#\^\&\*\(\)\=\+\[\{\]\}\\\|\;\:\'\"\,\.\<\>\/\?\s]+)/g}
    );
    
    // Other setup
    const validator = new ValidationProvider(context.workspaceState);
    validator.activate(context);
}
