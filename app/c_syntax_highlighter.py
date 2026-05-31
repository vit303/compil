from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PyQt6.QtCore import QRegularExpression


class CSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        keywords = [
            "auto", "break", "case", "char", "const", "continue", "default",
            "do", "double", "else", "enum", "extern", "float", "for", "goto",
            "if", "inline", "int", "long", "register", "return", "short",
            "signed", "sizeof", "static", "struct", "switch", "typedef",
            "union", "unsigned", "void", "volatile", "while",
            "__attribute__",
        ]

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569cd6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        for word in keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, keyword_format))

        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QColor("#c586c0"))
        self.highlighting_rules.append((
            QRegularExpression(r"^\s*#\s*\w+"),
            preprocessor_format,
        ))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#ce9178"))
        self.highlighting_rules.append((
            QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'),
            string_format,
        ))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a9955"))
        self.highlighting_rules.append((
            QRegularExpression(r"//.*"),
            comment_format,
        ))
        self.highlighting_rules.append((
            QRegularExpression(r"/\*[\s\S]*?\*/"),
            comment_format,
        ))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b5cea8"))
        self.highlighting_rules.append((
            QRegularExpression(r"\b[0-9]+(\.[0-9]+)?\b"),
            number_format,
        ))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
