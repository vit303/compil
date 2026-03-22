from dataclasses import dataclass
import difflib
import re
from typing import List, Tuple, Dict, Optional


@dataclass
class Token:
    code: int
    type_name: str
    lexeme: str
    line: int
    start_col: int
    end_col: int


class LexicalAnalyzer:
    def __init__(self):
        self.keywords = {
            "struct", "pub",
            "bool", "char", "str", "String",
            "i8", "i16", "i32", "i64", "i128", "isize",
            "u8", "u16", "u32", "u64", "u128", "usize",
            "f32", "f64",
        }

        self.operators_punct = {
            "=", "!", "<", ">", "+", "-", "*", "/", "%", "&", "|", "^", "~", "?", ":",
            ",", ";", ".", "(", ")", "{", "}", "[", "]",
            "->", "=>", "..", "...", "::", "==", "!=", "<=", ">=", "&&", "||", "<<", ">>",
        }

        self._primitive_lexemes = frozenset({
            "bool", "char", "str", "String",
            "i8", "i16", "i32", "i64", "i128", "isize",
            "u8", "u16", "u32", "u64", "u128", "usize",
            "f32", "f64",
        })
        self._primitive_numeric_re = re.compile(
            r"^i(8|16|32|64|128|size)$|^u(8|16|32|64|128|size)$|^f(32|64)$"
        )
        self._iu_letter_blob_re = re.compile(r"^[iu][a-zA-Z]{2,4}$")

        self._keyword_lower_vocab = sorted({k.lower() for k in self.keywords})

    def _canonical_keyword_for_lower(self, lower: str, lexeme: str) -> str:
        cands = [k for k in self.keywords if k.lower() == lower]
        if len(cands) == 1:
            return cands[0]
        if lexeme and lexeme[0].isupper():
            for k in cands:
                if k and k[0].isupper():
                    return k
        for k in cands:
            if k and k[0].islower():
                return k
        return cands[0]

    def _keyword_typo_message(self, lexeme: str) -> Optional[str]:
        if lexeme in self.keywords:
            return None
        if len(lexeme) < 3:
            return None
        if lexeme.startswith("_"):
            return None
        low = lexeme.lower()
        if low in {k.lower() for k in self.keywords}:
            return None
        if self._primitive_spelling_message(lexeme) is not None:
            return None
        matches = difflib.get_close_matches(
            low, self._keyword_lower_vocab, n=1, cutoff=0.86
        )
        if not matches:
            return None
        suggested_low = matches[0]
        ratio = difflib.SequenceMatcher(None, low, suggested_low).ratio()
        if ratio < 0.86:
            return None
        canonical = self._canonical_keyword_for_lower(suggested_low, lexeme)
        if canonical == lexeme:
            return None
        return (
            f"Возможная опечатка ключевого слова или зарезервированного имени: "
            f"имелось в виду «{canonical}»?"
        )

    def _primitive_spelling_message(self, lexeme: str) -> Optional[str]:
        if lexeme in self._primitive_lexemes:
            return None
        if re.match(r"^[iu][0-9]+$", lexeme):
            if not self._primitive_numeric_re.match(lexeme):
                return (
                    f"Неверное написание целочисленного типа «{lexeme}». "
                    f"Допустимы: i8, i16, i32, i64, i128, isize и аналогично u*."
                )
            return None
        if re.match(r"^f[0-9]+$", lexeme):
            if lexeme not in ("f32", "f64"):
                return (
                    f"Неверное написание типа с плавающей точкой «{lexeme}». "
                    f"Допустимы только f32 и f64."
                )
            return None
        if self._iu_letter_blob_re.match(lexeme) and lexeme not in ("isize", "usize"):
            return (
                f"Неизвестное написание встроенного типа «{lexeme}». "
                f"Проверьте написание (например, i32, u64, isize, usize)."
            )
        return None

    def _append_spelling_errors(self, tokens: List[Token], errors: List[Dict]) -> None:
        for t in tokens:
            if t.type_name != "идентификатор":
                continue
            msg = self._primitive_spelling_message(t.lexeme)
            if msg is None:
                msg = self._keyword_typo_message(t.lexeme)
            if msg is None:
                continue
            errors.append({
                "line": t.line,
                "col": t.start_col,
                "message": msg,
                "fragment": t.lexeme,
            })

    def analyze(self, text: str) -> Tuple[List[Token], List[Dict]]:
        tokens: List[Token] = []
        errors: List[Dict] = []

        i = 0
        n = len(text)
        line = 1
        col = 1

        while i < n:
            start_line = line
            start_col = col
            c = text[i]

            if c.isspace():
                if c == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                i += 1
                continue

            if c.isalpha() or c == '_' or (c == "'" and i+1 < n and text[i+1].isalpha()):
                j = i
                if c == "'":
                    j += 1
                while j < n and (text[j].isalnum() or text[j] in "_'"):
                    j += 1
                lexeme = text[i:j]

                if lexeme in self.keywords:
                    ttype = "ключевое слово"
                    code = 14
                elif lexeme.startswith("'") and len(lexeme) >= 2:
                    ttype = "lifetime"
                    code = 15
                else:
                    ttype = "идентификатор"
                    code = 2

                tokens.append(Token(code, ttype, lexeme, start_line, start_col, start_col + (j - i) - 1))
                consumed = j - i
                i = j
                col += consumed
                continue

            if c.isdigit() or (c == '-' and i+1 < n and text[i+1].isdigit()):
                j = i
                if c == '-':
                    j += 1
                while j < n and text[j].isdigit():
                    j += 1
                if j < n and text[j] == '.':
                    j += 1
                    while j < n and text[j].isdigit():
                        j += 1
                if j < n and text[j].lower() in 'e':
                    j += 1
                    if j < n and text[j] in '+-':
                        j += 1
                    while j < n and text[j].isdigit():
                        j += 1
                if j < n and text[j].isalpha():
                    k = j
                    while k < n and text[k].isalnum():
                        k += 1
                    suffix = text[j:k].lower()
                    if suffix in {"u8","u16","u32","u64","u128","usize",
                                  "i8","i16","i32","i64","i128","isize",
                                  "f32","f64"}:
                        j = k

                lexeme = text[i:j]
                tokens.append(Token(1, "литерал числа", lexeme, start_line, start_col, start_col + (j - i) - 1))
                consumed = j - i
                i = j
                col += consumed
                continue

            if c in ('"', 'r'):
                if c == 'r' and i+1 < n and text[i+1] in ('"', '#'):
                    j = i + 1
                    while j < n and text[j] != '"':
                        if text[j] == '\n':
                            line += 1
                            col = 1
                        else:
                            col += 1
                        j += 1
                    if j < n:
                        j += 1
                    lexeme = text[i:j]
                    tokens.append(Token(5, "строковый литерал", lexeme, start_line, start_col, start_col + (j - i) - 1))
                    consumed = j - i
                    i = j
                    col += consumed
                    continue
                elif c == '"':
                    j = i + 1
                    escaped = False
                    while j < n:
                        if escaped:
                            escaped = False
                            j += 1
                            continue
                        if text[j] == '\\':
                            escaped = True
                        elif text[j] == '"':
                            j += 1
                            break
                        if text[j] == '\n':
                            line += 1
                            col = 1
                        else:
                            col += 1
                        j += 1
                    lexeme = text[i:j]
                    tokens.append(Token(5, "строковый литерал", lexeme, start_line, start_col, start_col + (j - i) - 1))
                    consumed = j - i
                    i = j
                    col += consumed
                    continue

            if c == "'":
                j = i + 1
                if j < n and text[j] == '\\':
                    j += 2
                else:
                    j += 1
                if j < n and text[j] == "'":
                    j += 1
                lexeme = text[i:j]
                tokens.append(Token(6, "символьный литерал", lexeme, start_line, start_col, start_col + (j - i) - 1))
                consumed = j - i
                i = j
                col += consumed
                continue

            if c == '/' and i + 1 < n:
                if text[i + 1] == '/':
                    j = i
                    while j < n and text[j] != '\n':
                        j += 1
                    lexeme = text[i:j]
                    tokens.append(Token(8, "комментарий", lexeme, start_line, start_col, start_col + (j - i) - 1))
                    i = j
                    continue
                elif text[i + 1] == '*':
                    j = i + 2
                    while j < n - 1:
                        if text[j] == '*' and text[j + 1] == '/':
                            j += 2
                            break
                        if text[j] == '\n':
                            line += 1
                            col = 1
                        else:
                            col += 1
                        j += 1
                    lexeme = text[i:j]
                    tokens.append(Token(8, "комментарий", lexeme, start_line, start_col, start_col + (j - i) - 1))
                    consumed = j - i
                    i = j
                    col += consumed
                    continue

            if c == '#' and i + 1 < n and text[i + 1] == '[':
                j = i
                depth = 1
                j += 2
                while j < n and depth > 0:
                    if text[j] == '[':
                        depth += 1
                    elif text[j] == ']':
                        depth -= 1
                    if text[j] == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
                    j += 1
                lexeme = text[i:j]
                tokens.append(Token(9, "атрибут", lexeme, start_line, start_col, start_col + (j - i) - 1))
                consumed = j - i
                i = j
                col += consumed
                continue

            found = False
            for length in range(3, 0, -1):
                if i + length <= n:
                    op = text[i:i + length]
                    if op in self.operators_punct:
                        ttype = "оператор" if op not in {",",";",":",".","{","}","(",")","[","]"} else "разделитель"
                        code = 10 if ttype == "оператор" else 16
                        tokens.append(Token(code, ttype, op, start_line, start_col, start_col + length - 1))
                        i += length
                        col += length
                        found = True
                        break
            if found:
                continue

            errors.append({
                "line": start_line,
                "col": start_col,
                "message": f"Недопустимый символ {repr(c)}",
                "fragment": c
            })
            i += 1
            col += 1

        self._append_spelling_errors(tokens, errors)
        return tokens, errors
