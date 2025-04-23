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

import vscode = require( 'vscode' );

export enum SymbolType
{
    UNKNOWN,
    VARIABLE_TYPE_BEGIN,
    VARIABLE_INTEGR = VARIABLE_TYPE_BEGIN,
    VARIABLE_REAL,
    VARIABLE_STRING,
    VARIABLE_INTEGR_ARRAY,
    VARIABLE_REAL_ARRAY,
    VARIABLE_STRING_ARRAY,
    VARIABLE_TYPE_END = VARIABLE_STRING_ARRAY,

    CALLBACK,
    USER_FUNCTION
}

/**
 * General Symbol information for KSP
 */
export class Symbol
{
    public name                 : string = "";
    public symbolType        : SymbolType = SymbolType.UNKNOWN;
    public variableTypeName     : string  = "";
    public isConst              : boolean = false;
    public isPolyphonic         : boolean = false;
    public isUI                 : boolean = false;
    public uiVariableName       : string  = ""; // if isUI == true and type == callback, set a uiVariable Name
    public uiVariableType       : string  = ""; // if isUI == true and type == callback, set a UI type Name
    public description          : string  = "";
    public lineNumber           : number  = -1;
    public column               : number  = -1;

    public toVariableNameFormat( isUI : boolean = false ) : string
    {
        let ret = this.name;
        if( isUI )
        {
            ret = this.uiVariableName;
        }

        switch( this.symbolType )
        {
            case SymbolType.VARIABLE_INTEGR:         return '$' + ret;
            case SymbolType.VARIABLE_REAL:           return '~' + ret;
            case SymbolType.VARIABLE_STRING:         return '@' + ret;
            case SymbolType.VARIABLE_INTEGR_ARRAY:   return '%' + ret;
            case SymbolType.VARIABLE_REAL_ARRAY:     return '?' + ret;
            case SymbolType.VARIABLE_STRING_ARRAY:   return '!' + ret;
            case SymbolType.CALLBACK:                return '$' + ret;
            default:  return ret;
        }
    }

    static variableTypeChar2Type( char : string ) : SymbolType
    {
        switch( char )
        {
            case '$': return SymbolType.VARIABLE_INTEGR;
            case '~': return SymbolType.VARIABLE_REAL;
            case '@': return SymbolType.VARIABLE_STRING;
            case '%': return SymbolType.VARIABLE_INTEGR_ARRAY;
            case '?': return SymbolType.VARIABLE_REAL_ARRAY;
            case '!': return SymbolType.VARIABLE_STRING_ARRAY;
            default:  return SymbolType.UNKNOWN;
        }
    }

    static variableTypeChar2String( char : string ) : string
    {
        switch( char )
        {
            case '$': return "Integer";
            case '~': return "Real";
            case '@': return "String";
            case '%': return "Integer Array";
            case '?': return "Real Array";
            case '!': return "String Array";
            default:  return "Unkown";
        }
    }

    static variableType2Char( type : SymbolType ) : string
    {
        switch( type )
        {
            case SymbolType.VARIABLE_INTEGR:         return '$';
            case SymbolType.VARIABLE_REAL:           return '~';
            case SymbolType.VARIABLE_STRING:         return '@';
            case SymbolType.VARIABLE_INTEGR_ARRAY:   return '%';
            case SymbolType.VARIABLE_REAL_ARRAY:     return '?';
            case SymbolType.VARIABLE_STRING_ARRAY:   return '!';
            default:  return "Unkown";
        }
    }

    static isVariable( name : string ) : boolean
    {
        const type : SymbolType = Symbol.variableTypeChar2Type( name.charAt( 0 ) );
        switch( type )
        {
            case SymbolType.VARIABLE_INTEGR:
            case SymbolType.VARIABLE_REAL:
            case SymbolType.VARIABLE_STRING:
            case SymbolType.VARIABLE_INTEGR_ARRAY:
            case SymbolType.VARIABLE_REAL_ARRAY:
            case SymbolType.VARIABLE_STRING_ARRAY:
                return true;
            default:
                return false;
        }
    }

    static isArrayVariable( type: SymbolType ) : boolean
    {
        switch( type )
        {
            case SymbolType.VARIABLE_INTEGR_ARRAY:
            case SymbolType.VARIABLE_REAL_ARRAY:
            case SymbolType.VARIABLE_STRING_ARRAY:
                return true;
            default:
                return false;
        }
    }
}

/**
 * Symbol information for KSP (vscode.SymbolInformation extension)
 */
export class SymbolInformation extends vscode.SymbolInformation
{
    private symbol: Symbol;
    public range: vscode.Range | undefined          = undefined;
    public selectionRange: vscode.Range | undefined = undefined;

    constructor( name: string,
                 kind: vscode.SymbolKind,
                 containerName: string,
                 location: vscode.Location,
                 range?: vscode.Range,
                 selectionRange?: vscode.Range )
    {
        super( name, kind,containerName, location );
        this.containerName              = containerName;
        this.symbol                  = new Symbol();
        this.symbol.description      = containerName;
        this.range                      = range;
        this.selectionRange             = selectionRange;
    }

    public setKspSymbolValue( lineNumber : number, column : number, isConst : boolean, isPolyphonic : boolean, isUI : boolean, type : SymbolType, vaiableTypeName: string = "" )
    {
        this.symbol.name          = this.name;
        this.symbol.lineNumber    = lineNumber;
        this.symbol.column         = column;
        this.symbol.isConst       = isConst;
        this.symbol.isPolyphonic  = isPolyphonic;
        this.symbol.isUI          = isUI;
        this.symbol.symbolType = type;
        this.symbol.variableTypeName = vaiableTypeName;
    }

    public isVariable() : boolean
    {
        switch( this.symbol.symbolType )
        {
            case SymbolType.VARIABLE_INTEGR:
            case SymbolType.VARIABLE_REAL:
            case SymbolType.VARIABLE_STRING:
            case SymbolType.VARIABLE_INTEGR_ARRAY:
            case SymbolType.VARIABLE_REAL_ARRAY:
            case SymbolType.VARIABLE_STRING_ARRAY:
                return true;
            default:
                return false;
        }
    }

    public isUserFunction() : boolean
    {
        switch( this.symbol.symbolType )
        {
            case SymbolType.USER_FUNCTION:
                return true;
            default:
                return false;
        }
    }

    get Symbol() : Symbol { return this.symbol; }

}

export class SymbolUtil
{
    public static readonly REGEX_SYMBOL_BOUNDARY : RegExp     = /[\s|\(|\)|\{|\}|:|\[|\]|,|\+|-|\/|\*|<|>|\^|"]+/g
    public static readonly REGEX_SYMBOL_BOUNDARY_STR : string = "[\\s|\\(|\\)|\\{|\\}|:|\\[|\\]|,|\\+|-|\\/|\\*|<|>|\\^|\\\"]+";

    static startAt( lineText:string, position:vscode.Position ) : number
    {
        for( let i = position.character - 1; i >= 0; i-- )
        {
            let regex : RegExp = new RegExp( SymbolUtil.REGEX_SYMBOL_BOUNDARY );
            let char  = lineText.charAt( i );
            let match = regex.exec( char );
            if( match )
            {
                return i + 1;
            }
        }
        return position.character;
    }

    static endAt( lineText:string, position:vscode.Position ) : number
    {
        for( let i = position.character + 1; i < lineText.length; i++ )
        {
            let regex : RegExp = new RegExp( SymbolUtil.REGEX_SYMBOL_BOUNDARY );
            let char  = lineText.charAt( i );
            let match = regex.exec( char );
            if( match )
            {
                return i - 1;
            }
        }
        return position.character;
    }

    static parseSymbolAt( document: vscode.TextDocument, position: vscode.Position ) : string
    {
        let textLine : vscode.TextLine = document.lineAt( position.line );
        let line   : string = textLine.text;
        let eolPos : number = line.length;
        let symbol : string = "";
        for( let i = position.character; i < eolPos; i++ )
        {
            let regex : RegExp = SymbolUtil.REGEX_SYMBOL_BOUNDARY;
            let char  = line.charAt( i );
            let match = regex.exec( char );
            if( match )
            {
                if( char == '"' )
                {
                    // Literal String
                    symbol += '"';
                }
                break;
            }
            symbol += char;
        }
        for( let i = position.character - 1; i >= 0; i-- )
        {
            let regex : RegExp = SymbolUtil.REGEX_SYMBOL_BOUNDARY;
            let char  = line.charAt( i );
            let match = regex.exec( char );
            if( match )
            {
                if( char == '"' )
                {
                    // Literal String
                    symbol = '"' + symbol;
                }
                break;
            }
            symbol = char + symbol;
        }
        return symbol.trim();
    }

    static collect( document: vscode.TextDocument, endLineNumber: number = -1 ) : SymbolInformation[]
    {
        let result: SymbolInformation[] = [];

        // store for "on ui_control( <variable> )"
        let callBackUITypeNameTable: {[key:string]: string } = {}; // key: variable name, value: type

        let count = document.lineCount;
        if( endLineNumber >= 0 )
        {
            count = endLineNumber;
        }
        for( let i = 0; i < count; i++ )
        {
            let isConst: boolean = false;
            let range: vscode.Range | undefined         = undefined;
            let selectionRange: vscode.Range | undefined = undefined;

            //-----------------------------------------------------------------
            // check declare variables
            //-----------------------------------------------------------------
            {
                let DECLARE_REGEX = /^\s*declare\s+(ui_[a-zA-Z0-9_]+|const|polyphonic)?\s*([\$%~\?@!][a-zA-Z0-9_]+)/g;

                let text  = document.lineAt( i ).text;
                let match = DECLARE_REGEX.exec( text );
                if( match )
                {
                    isConst                         = Boolean(match[ 1 ] && match[ 1 ].toString() === "const");
                    let isPolyphonic                = Boolean(match[ 1 ] && match[ 1 ].toString() === "polyphonic");
                    let isUI                        = Boolean(match[ 1 ] && match[ 1 ].startsWith( "ui_" ));
                    let symKind: vscode.SymbolKind  = vscode.SymbolKind.Variable;
                    let name : string               = match[ 2 ];
                    let containerName : string      = "Variable";
                    let column : number             = text.indexOf( name );

                    let variableTypeChar            = name.charAt( 0 );
                    let variableTypeName : string   = Symbol.variableTypeChar2String( variableTypeChar );
                    let symbolType : SymbolType  = Symbol.variableTypeChar2Type( variableTypeChar );

                    range          = new vscode.Range( new vscode.Position( i, text.indexOf( "declare" ) ), new vscode.Position( i, Number.MAX_VALUE ) );
                    selectionRange = new vscode.Range( new vscode.Position( i, column ), new vscode.Position( i, Number.MAX_VALUE ) );

                    if( isConst )
                    {
                        containerName = "Constant Variable";
                        symKind = vscode.SymbolKind.Constant;
                    }
                    else if( isPolyphonic )
                    {
                        containerName = "Polyphonic Variable";
                    }
                    else if( isUI )
                    {
                        containerName = "UI Variable";
                        variableTypeName  = match[ 1 ].trim();
                        callBackUITypeNameTable[ name ] = variableTypeName;
                    }

                    let add = new SymbolInformation(
                        name.substr( 1 ),
                        symKind, containerName + " " + "(" + variableTypeName + ")",
                        new vscode.Location( document.uri, new vscode.Position( i, column ) ),
                        range,
                        selectionRange
                    );
                    add.setKspSymbolValue( i, text.indexOf( name ), isConst, isPolyphonic, isUI, symbolType, variableTypeName );
                    result.push( add );
                    continue;
                }
            } //~check declare variables
            //-----------------------------------------------------------------
            // check callback ( on #### )
            //-----------------------------------------------------------------
            {
                let DECLARE_REGEX = /^\s*(on\s+)([a-zA-Z0-9_]+)(\s*\(\s*[^\)]+\s*\))?/g;

                let text  = document.lineAt( i ).text;
                let match = DECLARE_REGEX.exec( text );
                if( match )
                {
                    let isUI                        = match[ 2 ] != undefined && match[ 3 ] != undefined && match[ 2 ].startsWith( "ui_" );
                    let uiName                      = null;
                    let symKind: vscode.SymbolKind  = vscode.SymbolKind.Function;
                    let name : string               = match[ 2 ];
                    let containerName : string      = "Callback";
                    let column : number             = text.indexOf( name );

                    range          = new vscode.Range( new vscode.Position( i, text.indexOf( "on " ) ), new vscode.Position( i, Number.MAX_VALUE ) );
                    selectionRange = new vscode.Range( new vscode.Position( i, column ), new vscode.Position( i, Number.MAX_VALUE ) );

                    if( !match[ 2 ] && !match[ 3 ] )
                    {
                        continue;
                    }

                    if( isUI )
                    {
                        uiName = match[ 3 ].replace( "(", "" ).replace( ")", "" ).trim();
                        containerName = "UI Callback for " + uiName;
                    }

                    let add = new SymbolInformation(
                        name,
                        symKind, containerName,
                        new vscode.Location( document.uri, new vscode.Position( i, column ) ),
                        range,
                        selectionRange
                    );
                    if( uiName )
                    {
                        if( callBackUITypeNameTable[ uiName ] )
                        {
                            add.Symbol.uiVariableType = callBackUITypeNameTable[ uiName ];
                        }
                        add.Symbol.uiVariableName = uiName.substr( 1 ) // [0] == variable type character
                    }

                    add.setKspSymbolValue( i, column, isConst, false, isUI, SymbolType.CALLBACK );
                    result.push( add );
                    continue;
                }
            } //~callback
            //-----------------------------------------------------------------
            // check user function ( function #### )
            //-----------------------------------------------------------------
            {
                let DECLARE_REGEX = /^\s*(function\s+)([a-zA-Z0-9_]+)/g;

                let text  = document.lineAt( i ).text;
                let match = DECLARE_REGEX.exec( text );
                if( match )
                {
                    let symKind: vscode.SymbolKind  = vscode.SymbolKind.Function;
                    let name : string               = match[ 2 ];
                    let containerName : string      = "Function";
                    let column : number             = text.indexOf( name );

                    range          = new vscode.Range( new vscode.Position( i, text.indexOf( "function " ) ), new vscode.Position( i, Number.MAX_VALUE ) );
                    selectionRange = new vscode.Range( new vscode.Position( i, column ), new vscode.Position( i, Number.MAX_VALUE ) );

                    let add = new SymbolInformation(
                        name,
                        symKind, containerName,
                        new vscode.Location( document.uri, new vscode.Position( i, column ) ),
                        range,
                        selectionRange
                    );

                    add.setKspSymbolValue( i, column, isConst, false, false, SymbolType.USER_FUNCTION );
                    result.push( add );
                    continue;
                }
            } //~function
        }

        return result;
    }
}
