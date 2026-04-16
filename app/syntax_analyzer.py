class SyntaxErrorEntry:
    def __init__(self, line, col, fragment, message):
        self.line = line
        self.col = col
        self.fragment = fragment
        self.message = message


class SyntaxAnalyzer:
    def analyze(self, text, lexical_errors=None):

        s = text
        n = len(s)
        i = 0
        line = 1
        col = 1
        errors = []
        lexical_error_entries = []

        def has_error_at(line_, col_, frag=None):
            for e in errors:
                if e.line == line_:
                    if e.col == col_:
                        return True
                    if frag is not None and e.fragment == frag:
                        return True
            return False
        if lexical_errors:
            for err in lexical_errors:
                entry = SyntaxErrorEntry(
                    err.get('line', 1),
                    err.get('col', 1),
                    err.get('fragment', ''),
                    err.get('message', '')
                )
                errors.append(entry)
                lexical_error_entries.append(entry)

        def peek():
            return s[i] if i < n else ""

        def adv():
            nonlocal i, line, col
            if i >= n:
                return
            c = s[i]
            i += 1
            if c == "\n":
                line += 1
                col = 1
            else:
                col += 1

        def err(msg, frag=None):
            if frag is None:
                frag = peek() if i < n else "<EOF>"
            errors.append(SyntaxErrorEntry(line, col, frag, msg))

        def skip_ws():
            nonlocal i
            while i < n and s[i] in " \t\n\r":
                adv()

        def read_identifier():
            nonlocal i
            start = i
            if i >= n:
                return None
            first = peek()
            if not (
                first.isalpha()
                or first in {"_"}
                or (first == "'" and i + 1 < n and s[i + 1].isalpha())
            ):
                return None

            adv()

            allowed_tail = set("_'@%?*!#^&()-")
            while i < n:
                ch = peek()
                if ch.isalnum() or ch == "_":
                    adv()
                    continue
                if ch in allowed_tail:
                    if ch == "#" and i + 1 < n and s[i + 1] == "[":
                        break
                    adv()
                    continue
                break

            return s[start:i]

        skip_ws()

        start_line = line
        start_col = col
        word = read_identifier()

        if word != "struct":
            if not has_error_at(start_line, start_col, word):
                err("Ожидалось ключевое слово 'struct'", word if word else "<EOF>")

        skip_ws()

        read_identifier()
        
        skip_ws()

        if peek() != "{":
            err("Ожидался символ '{'")
        else:
            adv()

        skip_ws()

        while i < n and peek() not in "};":
            skip_ws()
            if i >= n or peek() in "};":
                break

            field_name = read_identifier()
            
            if field_name is None:
                if peek() == "":
                    break
                if peek() == ":":
                    err("Лишний символ ':' (ожидалось имя поля)", ":")
                    adv()
                    skip_ws()
                    continue
                if peek().isspace():
                    skip_ws()
                    continue
                while i < n and peek() not in ",};\n":
                    adv()
                if peek() == ",":
                    adv()
                    skip_ws()
                continue

            skip_ws()

            # :
            if peek() == ":":
                adv()
            else:
                if peek() != "" and peek() not in ",};":
                    err("Ожидался символ ':'", ":")

            skip_ws()

            valid_types = {
                "bool", "char", "str", "String",
                "i8", "i16", "i32", "i64", "i128", "isize",
                "u8", "u16", "u32", "u64", "u128", "usize",
                "f32", "f64",
            }

            def has_lex_error_for_fragment(line_, start_col_, end_col_, fragment):
                for e in lexical_error_entries:
                    if e.line != line_:
                        continue
                    
                    if start_col_ <= e.col <= end_col_:
                        return True

                    if e.fragment == fragment:
                        return True

                return False

            type_line = line
            type_start_col = col

            if peek() == ":":
                err("Лишний символ ':' перед типом поля", ":")
                adv()
                skip_ws()

            type_name = read_identifier()

            type_end_col = col - 1

            if has_lex_error_for_fragment(type_line, type_start_col, type_end_col, type_name):
                pass
            else:
                if type_name is None:
                    err("Ожидался тип поля")
                elif type_name not in valid_types:
                    err(f"Неизвестный тип '{type_name}'", type_name)

            skip_ws()


            if peek() == ",":
                adv()
                skip_ws()
            elif peek() == "}":
                break
            elif peek() != "":
                next_ch = peek()
                if (
                    next_ch.isalpha()
                    or next_ch in {"_", "@"}
                    or (next_ch == "'" and i + 1 < n and s[i + 1].isalpha())
                ):
                    err("Ожидалась запятая ',' после типа поля", ",")

        skip_ws()

        found_closing_brace = False
        if peek() == "}":
            adv()
            found_closing_brace = True
        else:
            err("Ожидался символ '}'")

        skip_ws()

        if peek() == ";":
            adv()
        else:
            err("Ожидался символ ';' после '}'" if found_closing_brace else "Ожидался символ ';'")

        skip_ws()

        if i < n:
            err("Лишний код после окончания структуры")
        return errors