
from dataclasses import dataclass
from typing import List
from app.antlr_parser import (
    AntlrRustLexer, AntlrRustParser, Program
)


@dataclass
class SyntaxError:
    line: int
    column: int
    message: str
    fragment: str


class AntlrSyntaxAnalyzer:
    
    def analyze(self, text: str) -> List[SyntaxError]:
        errors = []

    
        lexer = AntlrRustLexer(text)
        token_stream = lexer.tokenize()

        # Collect lexer errors
        for error in lexer.errors:
            parts = error.split(": ", 1)
            if len(parts) == 2:
                line_info = parts[0]
                msg = parts[1]
                try:
                    coords = line_info.replace("Line ", "").split(":")
                    line = int(coords[0])
                    col = int(coords[1]) if len(coords) > 1 else 1
                except (ValueError, IndexError):
                    line, col = 1, 1
            else:
                line, col = 1, 1
                msg = error

            errors.append(SyntaxError(
                line=line,
                column=col,
                message=msg,
                fragment=""
            ))

        parser = AntlrRustParser(token_stream)
        ast = parser.parse()
        
        for error in parser.errors:
            line = 1
            col = 1
            msg = error
            
            if error.startswith("Line "):
                parts = error.split(": ", 1)
                line_part = parts[0]
                msg = parts[1] if len(parts) > 1 else error
                
                if ":" in line_part:
                    coords = line_part.replace("Line ", "").split(":")
                    try:
                        line = int(coords[0])
                        col = int(coords[1])
                    except (ValueError, IndexError):
                        try:
                            line = int(line_part.split()[-1])
                        except ValueError:
                            pass
                else:
                    try:
                        line = int(line_part.split()[-1])
                    except ValueError:
                        pass

            fragment = ""
            if "'" in msg:
                try:
                    start = msg.index("'") + 1
                    end = msg.index("'", start)
                    fragment = msg[start:end]
                except ValueError:
                    pass

            errors.append(SyntaxError(
                line=line,
                column=col,
                message=msg,
                fragment=fragment
            ))

        return errors

    def get_ast(self, text: str) -> Program:
        lexer = AntlrRustLexer(text)
        token_stream = lexer.tokenize()
        parser = AntlrRustParser(token_stream)
        return parser.parse()

    def format_errors(self, errors: List[SyntaxError]) -> str:
        if not errors:
            return "✓ Valid syntax"
        
        lines = []
        for err in sorted(errors, key=lambda e: (e.line, e.column)):
            location = f"Line {err.line}, Col {err.column}"
            lines.append(f"{location}: {err.message}")
        
        return "\n".join(lines)

