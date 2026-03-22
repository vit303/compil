from app.antlr_syntax_analyzer import AntlrSyntaxAnalyzer, SyntaxError


class SyntaxErrorEntry:
    def __init__(self, line, col, fragment, message):
        self.line = line
        self.col = col
        self.fragment = fragment
        self.message = message


TYPES = [
    "i128", "i64", "i32", "i16", "i8", "isize",
    "u128", "u64", "u32", "u16", "u8", "usize",
    "String", "f64", "f32", "bool", "char", "str",
]


class SyntaxAnalyzer:
    def __init__(self):
        self.antlr = AntlrSyntaxAnalyzer()

    def analyze(self, text: str):
        errors = self.antlr.analyze(text)
        
        result = []
        for err in errors:
            result.append(SyntaxErrorEntry(
                line=err.line,
                col=err.column,
                fragment=err.fragment,
                message=err.message
            ))
        
        return result


