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
    def analyze(self, text):
        s = text
        n = len(s)
        i = 0
        line = 1
        col = 1
        errors = []

        def peek():
            if i >= n:
                return ""
            return s[i]

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
            while i < n and s[i] in " \t\n\r":
                adv()

        def set_i(new_i):
            nonlocal i, line, col
            if new_i < 0:
                new_i = 0
            if new_i > n:
                new_i = n
            i = new_i
            line = 1
            col = 1
            k = 0
            while k < i:
                if s[k] == "\n":
                    line += 1
                    col = 1
                else:
                    col += 1
                k += 1

        def recover_struct():
            while i < n:
                j = s.find("struct", i)
                if j < 0:
                    set_i(n)
                    return
                if j > 0 and (s[j - 1].isalnum() or s[j - 1] == "_"):
                    set_i(j + 1)
                    continue
                after = j + 6
                if after < n and (s[after].isalnum() or s[after] == "_"):
                    set_i(j + 1)
                    continue
                set_i(j)
                return

        while True:
            skip_ws()
            if i >= n:
                break

            bad = False

            if not s.startswith("struct", i):
                err("Ожидалось ключевое слово 'struct'")
                recover_struct()
                continue

            for _ in range(6):
                adv()

            if peek() != " ":
                err("Ожидался пробел после 'struct' (правило <SPACE>)")
                recover_struct()
                continue
            adv()

            if not peek().isalpha():
                err("Ожидалась буква в начале имени структуры (<NAME_STRUCT>)")
                recover_struct()
                continue
            adv()

            while i < n:
                c = peek()
                if c in " \t\n\r":
                    saved = i
                    while i < n and s[i] in " \t\n\r":
                        adv()
                    if peek() == "{":
                        continue
                    set_i(saved)
                    err("В имени структуры не допускаются пробелы")
                    bad = True
                    break
                if c.isalpha() or c.isdigit() or c == "_":
                    adv()
                elif c == "{":
                    adv()
                    break
                else:
                    err("Ожидалась буква, цифра, '_' или '{' в имени структуры")
                    bad = True
                    break
            else:
                err("Незавершённое имя структуры: ожидалось '{'", "<EOF>")
                bad = True

            if bad:
                recover_struct()
                continue

            skip_ws()
            if peek() == "}":
                adv()
                skip_ws()
                if peek() == ";":
                    adv()
                else:
                    err("Ожидалось ';' после '}' (<END_BODY>)")
                    recover_struct()
                continue

            fields_done = False
            while not fields_done:
                c = peek()
                if not c.isalpha():
                    err("Ожидалась буква в начале имени поля (<BODY>)")
                    recover_struct()
                    fields_done = True
                    continue
                adv()

                id_bad = False
                while i < n:
                    c = peek()
                    if c.isalpha() or c.isdigit() or c == "_":
                        adv()
                    elif c == ":":
                        adv()
                        break
                    else:
                        err("Ожидалась буква, цифра, '_' или ':' (<ID>)")
                        id_bad = True
                        break
                else:
                    err("Незавершённый идентификатор поля: ожидалось ':'", "<EOF>")
                    id_bad = True

                if id_bad:
                    recover_struct()
                    fields_done = True
                    continue

                skip_ws()
                if i >= n:
                    err("Ожидался тип поля (<TYPE>)", "<EOF>")
                    recover_struct()
                    fields_done = True
                    continue

                ok = False
                tline, tcol = line, col
                for t in TYPES:
                    if s.startswith(t, i):
                        end = i + len(t)
                        if end < n:
                            nx = s[end]
                            if nx.isalnum() or nx == "_":
                                continue
                        for _ in t:
                            adv()
                        ok = True
                        break

                if not ok:
                    j = i
                    while j < n and (s[j].isalnum() or s[j] == "_"):
                        j += 1
                    badw = s[i:j] if j > i else peek()
                    msg = (
                        "Недопустимый тип «" + badw + "» (<TYPE>). "
                        "См. список TYPES в syntax_analyzer.py"
                    )
                    errors.append(SyntaxErrorEntry(tline, tcol, badw, msg))
                    set_i(j)
                    recover_struct()
                    fields_done = True
                    continue

                skip_ws()
                c = peek()
                if c == ",":
                    adv()
                    skip_ws()
                    continue
                if c == "}":
                    adv()
                    skip_ws()
                    if peek() == ";":
                        adv()
                    else:
                        err("Ожидалось ';' после '}' (<END_BODY>)")
                        recover_struct()
                    fields_done = True
                    continue

                err("Ожидалось ',' или '}' после типа (<END_FIELD>)")
                recover_struct()
                fields_done = True

        return errors
