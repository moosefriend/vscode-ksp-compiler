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
import * as config from './configurationConstants';

export class ConfigurationManager {
    /**
     * ctor
     */
    private constructor() { }

    /**
     * Get a user configuration value
     */
    static getConfig<T>(key: string, defaultValue: T): T {
        let ret: T = defaultValue;
        ConfigurationManager.getConfigComplex(key, defaultValue, (v, u) => {
            ret = v;
        });
        return ret;
    }

    /**
     * Get a user configuration value
     */
    static getConfigComplex<T>(key: string, defaultValue: T, callback: (value: T, userDefined: boolean) => void): void {
        let section: vscode.WorkspaceConfiguration = vscode.workspace.getConfiguration(config.CONFIG_SECTION_NAME);
        let value: T = defaultValue;
        let userDefined: boolean = false;
        let inspect = section.inspect<T>(key);

        if (!section) {
            callback(defaultValue, userDefined);
            return;
        }

        if (inspect) {
            if (inspect.workspaceValue !== undefined && inspect.workspaceValue !== null) {
                value = inspect.workspaceValue;
                userDefined = true;
            }
            else if (inspect.globalValue !== undefined && inspect.globalValue !== null) {
                value = inspect.globalValue;
            }
        }
        callback(value, userDefined);
    }
}