lexer grammar RustLexer;

// Keywords
STRUCT: 'struct';
PUB: 'pub';

// Primitive types
BOOL: 'bool';
CHAR: 'char';
STR: 'str';
STRING: 'String';

// Integer types
I8: 'i8';
I16: 'i16';
I32: 'i32';
I64: 'i64';
I128: 'i128';
ISIZE: 'isize';

U8: 'u8';
U16: 'u16';
U32: 'u32';
U64: 'u64';
U128: 'u128';
USIZE: 'usize';

// Float types
F32: 'f32';
F64: 'f64';

// Delimiters
LBRACE: '{';
RBRACE: '}';
LPAREN: '(';
RPAREN: ')';
LBRACKET: '[';
RBRACKET: ']';
SEMICOLON: ';';
COMMA: ',';
COLON: ':';
ARROW: '->';

// Identifier and numbers
IDENT: [a-zA-Z_][a-zA-Z0-9_]*;
NUMBER: [0-9]+ ('.' [0-9]+)?;

// Whitespace and comments
WS: [ \t\r\n]+ -> skip;
LINE_COMMENT: '//' ~[\r\n]* -> skip;
BLOCK_COMMENT: '/*' .*? '*/' -> skip;

// Unknown character (for error handling)
UNKNOWN: .;
