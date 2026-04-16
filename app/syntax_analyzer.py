class SyntaxErrorEntry:
    def __init__(self, line, col, fragment, message):
        self.line = line
        self.col = col
        self.fragment = fragment
        self.message = message


class SyntaxAnalyzer:
    def analyze(self, text, lexical_errors=None):
        """
        Принимает текст и список ошибок от лексера.
        Лексер уже находит опечатки в ключевых словах и типах.
        Парсер добавляет только синтаксические ошибки.
        """
        s = text
        n = len(s)
        i = 0
        line = 1
        col = 1
        errors = []

        def has_error_at(line_, col_, frag=None):
            for e in errors:
                if e.line == line_:
                    # если совпадает позиция — ок
                    if e.col == col_:
                        return True
                    # если совпадает текст ошибки — тоже считаем дубликатом
                    if frag is not None and e.fragment == frag:
                        return True
            return False
        # Получаем ошибки лексера, если они есть
        if lexical_errors:
            for err in lexical_errors:
                errors.append(SyntaxErrorEntry(
                    err.get('line', 1),
                    err.get('col', 1),
                    err.get('fragment', ''),
                    err.get('message', '')
                ))

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
            if i >= n or not peek().isalpha():
                return None
            adv()
            while i < n and (peek().isalnum() or peek() == "_"):
                adv()
            return s[start:i]

        # НАЧАЛО АНАЛИЗА
        skip_ws()

        # Пропускаем ключевое слово struct (лексер уже проверил опечатки)
        # Читаем первое слово
        start_line = line
        start_col = col
        word = read_identifier()

        if word != "struct":
            if not has_error_at(start_line, start_col, word):
                err("Ожидалось ключевое слово 'struct'", word if word else "<EOF>")

        skip_ws()

        # Имя структуры
        read_identifier()
        
        skip_ws()

        # Проверяем {
        if peek() != "{":
            err("Ожидался символ '{'")
        else:
            adv()

        skip_ws()

        # ТЕЛО СТРУКТУРЫ
        while i < n and peek() not in "};":
            # Читаем имя поля
            field_name = read_identifier()
            
            if field_name is None:
                if peek() == "":
                    break
                # Пропускаем до запятой или }
                while i < n and peek() not in ",};":
                    adv()
                if peek() == ",":
                    adv()
                    skip_ws()
                continue

            skip_ws()

            # :
            if peek() == ":":
                adv()

            skip_ws()

            # Список допустимых типов
            valid_types = {
                "bool", "char", "str", "String",
                "i8", "i16", "i32", "i64", "i128", "isize",
                "u8", "u16", "u32", "u64", "u128", "usize",
                "f32", "f64",
            }

            def has_lex_error_for_fragment(line_, start_col_, end_col_, fragment):
                for e in errors:
                    if e.line != line_:
                        continue
                    
                    # 1. Ошибка попадает в диапазон
                    if start_col_ <= e.col <= end_col_:
                        return True

                    # 2. Или совпадает текст (важно для u65)
                    if e.fragment == fragment:
                        return True

                return False

            type_line = line
            type_col = col
            
            type_start_col = col

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

            # , или }
            if peek() == ",":
                adv()
                skip_ws()
            elif peek() == "}":
                break

        # Пропускаем всё остальное до конца
        skip_ws()

        # Проверка }
        found_closing_brace = False
        if peek() == "}":
            adv()
            found_closing_brace = True
        else:
            err("Ожидался символ '}'")

        skip_ws()

        # Проверка ;
        if peek() == ";":
            adv()
        else:
            err("Ожидался символ ';' после '}'" if found_closing_brace else "Ожидался символ ';'")

        skip_ws()

        # Лишний код
        if i < n:
            err("Лишний код после окончания структуры")
        return errors