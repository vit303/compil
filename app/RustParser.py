# Generated from RustParser.g4 by ANTLR 4.13.0
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,36,43,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,1,0,5,0,12,8,0,
        10,0,12,0,15,9,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,2,
        5,2,29,8,2,10,2,12,2,32,9,2,1,2,3,2,35,8,2,1,3,1,3,1,3,1,3,1,4,1,
        4,1,4,0,0,5,0,2,4,6,8,0,1,2,0,3,20,31,31,40,0,13,1,0,0,0,2,18,1,
        0,0,0,4,25,1,0,0,0,6,36,1,0,0,0,8,40,1,0,0,0,10,12,3,2,1,0,11,10,
        1,0,0,0,12,15,1,0,0,0,13,11,1,0,0,0,13,14,1,0,0,0,14,16,1,0,0,0,
        15,13,1,0,0,0,16,17,5,0,0,1,17,1,1,0,0,0,18,19,5,1,0,0,19,20,5,31,
        0,0,20,21,5,21,0,0,21,22,3,4,2,0,22,23,5,22,0,0,23,24,5,27,0,0,24,
        3,1,0,0,0,25,30,3,6,3,0,26,27,5,28,0,0,27,29,3,6,3,0,28,26,1,0,0,
        0,29,32,1,0,0,0,30,28,1,0,0,0,30,31,1,0,0,0,31,34,1,0,0,0,32,30,
        1,0,0,0,33,35,5,28,0,0,34,33,1,0,0,0,34,35,1,0,0,0,35,5,1,0,0,0,
        36,37,5,31,0,0,37,38,5,29,0,0,38,39,3,8,4,0,39,7,1,0,0,0,40,41,7,
        0,0,0,41,9,1,0,0,0,3,13,30,34
    ]

class RustParser ( Parser ):

    grammarFileName = "RustParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'struct'", "'pub'", "'bool'", "'char'", 
                     "'str'", "'String'", "'i8'", "'i16'", "'i32'", "'i64'", 
                     "'i128'", "'isize'", "'u8'", "'u16'", "'u32'", "'u64'", 
                     "'u128'", "'usize'", "'f32'", "'f64'", "'{'", "'}'", 
                     "'('", "')'", "'['", "']'", "';'", "','", "':'", "'->'" ]

    symbolicNames = [ "<INVALID>", "STRUCT", "PUB", "BOOL", "CHAR", "STR", 
                      "STRING", "I8", "I16", "I32", "I64", "I128", "ISIZE", 
                      "U8", "U16", "U32", "U64", "U128", "USIZE", "F32", 
                      "F64", "LBRACE", "RBRACE", "LPAREN", "RPAREN", "LBRACKET", 
                      "RBRACKET", "SEMICOLON", "COMMA", "COLON", "ARROW", 
                      "IDENT", "NUMBER", "WS", "LINE_COMMENT", "BLOCK_COMMENT", 
                      "UNKNOWN" ]

    RULE_program = 0
    RULE_structDecl = 1
    RULE_fields = 2
    RULE_field = 3
    RULE_type_ = 4

    ruleNames =  [ "program", "structDecl", "fields", "field", "type_" ]

    EOF = Token.EOF
    STRUCT=1
    PUB=2
    BOOL=3
    CHAR=4
    STR=5
    STRING=6
    I8=7
    I16=8
    I32=9
    I64=10
    I128=11
    ISIZE=12
    U8=13
    U16=14
    U32=15
    U64=16
    U128=17
    USIZE=18
    F32=19
    F64=20
    LBRACE=21
    RBRACE=22
    LPAREN=23
    RPAREN=24
    LBRACKET=25
    RBRACKET=26
    SEMICOLON=27
    COMMA=28
    COLON=29
    ARROW=30
    IDENT=31
    NUMBER=32
    WS=33
    LINE_COMMENT=34
    BLOCK_COMMENT=35
    UNKNOWN=36

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(RustParser.EOF, 0)

        def structDecl(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RustParser.StructDeclContext)
            else:
                return self.getTypedRuleContext(RustParser.StructDeclContext,i)


        def getRuleIndex(self):
            return RustParser.RULE_program

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProgram" ):
                return visitor.visitProgram(self)
            else:
                return visitor.visitChildren(self)




    def program(self):

        localctx = RustParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 13
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 10
                self.structDecl()
                self.state = 15
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 16
            self.match(RustParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StructDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRUCT(self):
            return self.getToken(RustParser.STRUCT, 0)

        def IDENT(self):
            return self.getToken(RustParser.IDENT, 0)

        def LBRACE(self):
            return self.getToken(RustParser.LBRACE, 0)

        def fields(self):
            return self.getTypedRuleContext(RustParser.FieldsContext,0)


        def RBRACE(self):
            return self.getToken(RustParser.RBRACE, 0)

        def SEMICOLON(self):
            return self.getToken(RustParser.SEMICOLON, 0)

        def getRuleIndex(self):
            return RustParser.RULE_structDecl

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStructDecl" ):
                return visitor.visitStructDecl(self)
            else:
                return visitor.visitChildren(self)




    def structDecl(self):

        localctx = RustParser.StructDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_structDecl)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 18
            self.match(RustParser.STRUCT)
            self.state = 19
            self.match(RustParser.IDENT)
            self.state = 20
            self.match(RustParser.LBRACE)
            self.state = 21
            self.fields()
            self.state = 22
            self.match(RustParser.RBRACE)
            self.state = 23
            self.match(RustParser.SEMICOLON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FieldsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def field(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RustParser.FieldContext)
            else:
                return self.getTypedRuleContext(RustParser.FieldContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(RustParser.COMMA)
            else:
                return self.getToken(RustParser.COMMA, i)

        def getRuleIndex(self):
            return RustParser.RULE_fields

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFields" ):
                return visitor.visitFields(self)
            else:
                return visitor.visitChildren(self)




    def fields(self):

        localctx = RustParser.FieldsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_fields)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 25
            self.field()
            self.state = 30
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 26
                    self.match(RustParser.COMMA)
                    self.state = 27
                    self.field() 
                self.state = 32
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

            self.state = 34
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 33
                self.match(RustParser.COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FieldContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENT(self):
            return self.getToken(RustParser.IDENT, 0)

        def COLON(self):
            return self.getToken(RustParser.COLON, 0)

        def type_(self):
            return self.getTypedRuleContext(RustParser.Type_Context,0)


        def getRuleIndex(self):
            return RustParser.RULE_field

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitField" ):
                return visitor.visitField(self)
            else:
                return visitor.visitChildren(self)




    def field(self):

        localctx = RustParser.FieldContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_field)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 36
            self.match(RustParser.IDENT)
            self.state = 37
            self.match(RustParser.COLON)
            self.state = 38
            self.type_()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Type_Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BOOL(self):
            return self.getToken(RustParser.BOOL, 0)

        def CHAR(self):
            return self.getToken(RustParser.CHAR, 0)

        def STR(self):
            return self.getToken(RustParser.STR, 0)

        def STRING(self):
            return self.getToken(RustParser.STRING, 0)

        def I8(self):
            return self.getToken(RustParser.I8, 0)

        def I16(self):
            return self.getToken(RustParser.I16, 0)

        def I32(self):
            return self.getToken(RustParser.I32, 0)

        def I64(self):
            return self.getToken(RustParser.I64, 0)

        def I128(self):
            return self.getToken(RustParser.I128, 0)

        def ISIZE(self):
            return self.getToken(RustParser.ISIZE, 0)

        def U8(self):
            return self.getToken(RustParser.U8, 0)

        def U16(self):
            return self.getToken(RustParser.U16, 0)

        def U32(self):
            return self.getToken(RustParser.U32, 0)

        def U64(self):
            return self.getToken(RustParser.U64, 0)

        def U128(self):
            return self.getToken(RustParser.U128, 0)

        def USIZE(self):
            return self.getToken(RustParser.USIZE, 0)

        def F32(self):
            return self.getToken(RustParser.F32, 0)

        def F64(self):
            return self.getToken(RustParser.F64, 0)

        def IDENT(self):
            return self.getToken(RustParser.IDENT, 0)

        def getRuleIndex(self):
            return RustParser.RULE_type_

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitType_" ):
                return visitor.visitType_(self)
            else:
                return visitor.visitChildren(self)




    def type_(self):

        localctx = RustParser.Type_Context(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_type_)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 2149580792) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





