parser grammar RustParser;

options { tokenVocab=RustLexer; }

program: structDecl* EOF;

structDecl: STRUCT IDENT LBRACE fields RBRACE SEMICOLON;

fields: field (COMMA field)* COMMA?;

field: IDENT COLON type_;

type_: BOOL
     | CHAR
     | STR
     | STRING
     | I8
     | I16
     | I32
     | I64
     | I128
     | ISIZE
     | U8
     | U16
     | U32
     | U64
     | U128
     | USIZE
     | F32
     | F64
     | IDENT
     ;
