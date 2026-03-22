# Generated from RustParser.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .RustParser import RustParser
else:
    from RustParser import RustParser

# This class defines a complete generic visitor for a parse tree produced by RustParser.

class RustParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by RustParser#program.
    def visitProgram(self, ctx:RustParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RustParser#structDecl.
    def visitStructDecl(self, ctx:RustParser.StructDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RustParser#fields.
    def visitFields(self, ctx:RustParser.FieldsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RustParser#field.
    def visitField(self, ctx:RustParser.FieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RustParser#type_.
    def visitType_(self, ctx:RustParser.Type_Context):
        return self.visitChildren(ctx)



del RustParser