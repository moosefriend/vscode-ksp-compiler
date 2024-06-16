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
export const CONFIG_SECTION_NAME = 'ksp';

// KSP Compiler
export const KEY_PYTHON_LOCATION = 'python.location';
export const KEY_COMPILER_SCRIPT = 'compiler.script';
export const KEY_COMPACT = 'compiler.compact';
export const KEY_OBFUSCATE = 'compiler.obfuscate';
export const KEY_EXTRA_SYNTAX_CHECK = 'compiler.extra_syntax_check';
export const KEY_OPTIMIZE = 'compiler.optimize';
export const KEY_COMPILE_DATE = 'compiler.date';

// Validate
export const KEY_ENABLE_VALIDATE = 'validate.enable';
export const KEY_ENABLE_REALTIME_VALIDATE = 'validate.realtime.enable';
export const KEY_REALTIME_VALIDATE_DELAY = 'validate.realtime.delay';

export const DEFAULT_PYTHON_LOCATION = 'python';
export const DEFAULT_COMPACT = false;
export const DEFAULT_OBFUSCATE = false;
export const DEFAULT_EXTRA_SYNTAX_CHECK = false;
export const DEFAULT_OPTIMIZE = false;
export const DEFAULT_COMPILE_DATE = false;

export const DEFAULT_ENABLE_VALIDATE = false;
export const DEFAULT_REALTIME_VALIDATE = true;
export const DEFAULT_VALIDATE_DELAY = 500;