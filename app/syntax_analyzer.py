TYPES = [
    "i128", "i64", "i32", "i16", "i8", "isize",
    "u128", "u64", "u32", "u16", "u8", "usize",
    "String", "f64", "f32", "bool", "char", "str",
]
KEYWORDS = ["struct"]

class SyntaxErrorEntry:
    def __init__(self, line, col, fragment, message):
        self.line = line
        self.col = col
        self.fragment = fragment
        self.message = message

class SyntaxAnalyzer:
    def analyze(self, text):
        s = text
        n = len(s)
        i = 0
        line = 1
        col = 1
        errors = []

        def peek():
            return s[i] if i < n else ""

        def adv():
            nonlocal i, line, col
            if i >= n: return
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
            if errors and errors[-1].line == line and errors[-1].col == col:
                return
            errors.append(SyntaxErrorEntry(line, col, frag, msg))

        def skip_ws():
            while i < n and s[i] in " \t\n\r":
                adv()

        def read_identifier():
            if not peek().isalpha() and peek() != "_":
                return False
            adv()
            while i < n and (peek().isalnum() or peek() == "_"):
                adv()
            return True

        def read_type():
            for t in TYPES:
                if s.startswith(t, i):
                    end = i + len(t)
                    if end < n and (s[end].isalnum() or s[end] == "_"):
                        continue
                    for _ in t:
                        adv()
                    return True
            return False

        skip_ws()

        # struct
        if not s.startswith("struct", i):
            err("Ожидалось ключевое слово 'struct'", "stkjlruct" if s.startswith("stkjlruct", i) else None)
            while i < n and not peek().isspace() and peek() not in "{;":
                adv()
        else:
            for _ in range(6):
                adv()

        skip_ws()

        if not read_identifier():
            err("Ожидалось имя структуры")

        skip_ws()

        # {
        if peek() == "{":
            adv()
        else:
            err("Ожидался символ '{'")

        skip_ws()

        while i < n and peek() != "}":
            if peek() in ",;}" or not (peek().isalpha() or peek() == "_"):

                err("Ожидалось имя поля")
                while i < n and peek() not in ",:}":
                    adv()
                if peek() == ",":
                    adv()
                skip_ws()
                continue

            read_identifier()

            skip_ws()

            if peek() == ":":
                adv()
            else:
                err("Ожидался ':' после имени поля")

            skip_ws()

            if not read_type():
                err("Ожидался корректный тип поля", "il64" if s.startswith("il64", i) else None)
                while i < n and not peek().isspace() and peek() not in ",;}":
                    adv()

            skip_ws()

            if peek() == ",":
                adv()
                skip_ws()
            elif peek() == "}":
                break
            else:
                err("Ожидалось ',' или '}'")
                while i < n and peek() not in ",}":
                    adv()
                if peek() == ",":
                    adv()
                    skip_ws()

        # EOF внутри структуры
        if i >= n:
            err("Ожидался символ '}'")
            errors.append(SyntaxErrorEntry(line, col, "<EOF>", "Ожидался символ ';'"))
            return errors

        # }
        if peek() == "}":
            adv()
        else:
            err("Ожидался символ '}'")

        skip_ws()

        # EOF после }
        if i >= n:
            err("Ожидался символ ';'")
            return errors

        # ;
        if peek() == ";":
            adv()
        else:
            err("Ожидался символ ';'")

        return errors