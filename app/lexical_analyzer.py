from dataclasses import dataclass
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
    """Лексический анализатор для структур и связанных конструкций в Rust."""

    def __init__(self):
        self.keywords = {
            # Основные для структур
            "struct", "enum", "impl", "trait", "pub", "crate", "mod", "use", "where",
            "self", "Self", "super", "const", "static", "fn", "type", "let", "mut",
            "for", "in", "if", "else", "match", "return", "break", "continue",
            # Примитивы и часто используемые типы
            "bool", "char", "str", "String",
            "i8", "i16", "i32", "i64", "i128", "isize",
            "u8", "u16", "u32", "u64", "u128", "usize",
            "f32", "f64",
            # Часто в derive
            "Debug", "Clone", "Copy", "PartialEq", "Eq", "Hash", "Default",
        }

        self.operators_punct = {
            # Односимвольные
            "=", "!", "<", ">", "+", "-", "*", "/", "%", "&", "|", "^", "~", "?", ":",
            ",", ";", ".", "(", ")", "{", "}", "[", "]",
            # Многосимвольные (приоритет длинных)
            "->", "=>", "..", "...", "::", "==", "!=", "<=", ">=", "&&", "||", "<<", ">>",
        }

    def analyze(self, text: str) -> Tuple[List[Token], List[Dict]]:
        tokens: List[Token] = []
        errors: List[Dict] = []

        i = 0
        n = len(text)
        line = 1
        col = 1  # 1-based

        while i < n:
            start_line = line
            start_col = col
            c = text[i]

            # Пропускаем whitespace (не генерируем токены)
            if c.isspace():
                if c == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                i += 1
                continue

            # Идентификатор или ключевое слово (включая lifetime 'a)
            if c.isalpha() or c == '_' or (c == "'" and i+1 < n and text[i+1].isalpha()):
                j = i
                if c == "'":
                    j += 1  # пропускаем апостроф
                while j < n and (text[j].isalnum() or text[j] in "_'"):
                    j += 1
                lexeme = text[i:j]

                if lexeme in self.keywords:
                    ttype = "ключевое слово"
                    code = 14
                elif lexeme.startswith("'") and len(lexeme) >= 2:
                    ttype = "lifetime"
                    code = 15  # новый код для lifetime
                else:
                    ttype = "идентификатор"
                    code = 2

                tokens.append(Token(code, ttype, lexeme, start_line, start_col, start_col + (j - i) - 1))
                i = j
                col += j - i
                continue

            # Числа (целые, float, с суффиксами u64, i32, f64 и т.д.)
            if c.isdigit() or (c == '-' and i+1 < n and text[i+1].isdigit()):
                j = i
                if c == '-':
                    j += 1
                while j < n and text[j].isdigit():
                    j += 1
                # дробная часть
                if j < n and text[j] == '.':
                    j += 1
                    while j < n and text[j].isdigit():
                        j += 1
                # экспонента
                if j < n and text[j].lower() in 'e':
                    j += 1
                    if j < n and text[j] in '+-':
                        j += 1
                    while j < n and text[j].isdigit():
                        j += 1
                # суффикс типа (u8, i32, f64 и т.д.)
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
                i = j
                col += j - i
                continue

            # Строки "..." и raw-строки r"..." / r#"...# и т.д.
            if c in ('"', 'r'):
                if c == 'r' and i+1 < n and text[i+1] in ('"', '#'):
                    # raw string — упрощённо (не считаем вложенность #)
                    j = i + 1
                    while j < n and text[j] != '"':
                        if text[j] == '\n':
                            line += 1
                            col = 1
                        else:
                            col += 1
                        j += 1
                    if j < n:
                        j += 1  # закрывающая "
                    lexeme = text[i:j]
                    tokens.append(Token(5, "строковый литерал", lexeme, start_line, start_col, start_col + (j - i) - 1))
                    i = j
                    col += j - i
                    continue
                elif c == '"':
                    # обычная строка
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
                    i = j
                    col += j - i
                    continue

            # Символьные литералы 'c', '\n', '\xFF'
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
                i = j
                col += j - i
                continue

            # Комментарии
            if c == '/' and i + 1 < n:
                if text[i + 1] == '/':
                    # line comment
                    j = i
                    while j < n and text[j] != '\n':
                        j += 1
                    lexeme = text[i:j]
                    tokens.append(Token(8, "комментарий", lexeme, start_line, start_col, start_col + (j - i) - 1))
                    i = j
                    continue
                elif text[i + 1] == '*':
                    # block comment
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
                    i = j
                    col += j - i
                    continue

            # Атрибуты #[...]
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
                i = j
                col += j - i
                continue

            # Операторы и пунктуация
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

            # Неизвестный символ → ошибка
            errors.append({
                "line": start_line,
                "col": start_col,
                "message": f"Недопустимый символ {repr(c)}"
            })
            i += 1
            col += 1

        return tokens, errors