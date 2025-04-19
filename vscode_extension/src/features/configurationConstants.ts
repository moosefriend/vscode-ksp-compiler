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
export const KEY_FORCE = 'compiler.force';
export const KEY_COMPACT = 'compiler.compact';
export const KEY_COMPACT_VARIABLES = 'compiler.compact_variables';
export const KEY_COMBINE_CALLBACKS = 'compiler.combine_callbacks';
export const KEY_EXTRA_SYNTAX_CHECK = 'compiler.extra_syntax_check';
export const KEY_OPTIMIZE = 'compiler.optimize';
export const KEY_EXTRA_BRANCH_OPTIMIZATION = 'compiler.extra_branch_optimization';
export const KEY_INDENT_SIZE = 'compiler.indent_size';
export const KEY_ADD_COMPILE_DATE = 'compiler.add_compile_date';
export const KEY_COMPILE_DATE = 'compiler.date';
export const KEY_SANITIZE_EXIT_COMMAND = 'compiler.sanitize_exit_command';

// Validate
export const KEY_ENABLE_VALIDATE = 'validate.enable';
export const KEY_ENABLE_REALTIME_VALIDATE = 'validate.realtime.enable';
export const KEY_REALTIME_VALIDATE_DELAY = 'validate.realtime.delay';

export const DEFAULT_PYTHON_LOCATION = 'python';
export const DEFAULT_FORCE = false;
export const DEFAULT_COMPACT = false;
export const DEFAULT_COMPACT_VARIABLES = false;
export const DEFAULT_COMBINE_CALLBACKS = false;
export const DEFAULT_EXTRA_SYNTAX_CHECK = false;
export const DEFAULT_OPTIMIZE = false;
export const DEFAULT_EXTRA_BRANCH_OPTIMIZATION = false;
export const DEFAULT_INDENT_SIZE = 4;
export const DEFAULT_ADD_COMPILE_DATE = false;
export const DEFAULT_SANITIZE_EXIT_COMMAND = false;

export const DEFAULT_VALIDATE_ENABLE = false;
export const DEFAULT_VALIDATE_DELAY = 500;