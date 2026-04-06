

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

KEYWORDS = ["struct"]

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

        def read_identifier():
            nonlocal i
            start = i

            if not peek().isalpha():
                return None

            adv()
            while i < n and (peek().isalnum() or peek() == "_"):
                adv()

            return s[start:i]

        def read_type():
            nonlocal i
            for t in TYPES:
                if s.startswith(t, i):
                    end = i + len(t)
                    if end < n and (s[end].isalnum() or s[end] == "_"):
                        continue
                    for _ in t:
                        adv()
                    return True
            return False

        # =======================
        # START
        # =======================
        skip_ws()
        flag = True
        if not s.startswith("struct", i):
            err("Ожидалось ключевое слово 'struct'")
            flag = False
            while i < n and peek() != "{":
                adv()
            
        else:
            for _ in range(6):
                adv()
        # SPACE
        if flag == True:
            space_count = 0
            while peek() == " ":
                adv()
                space_count += 1
        
            if space_count == 0:
                err("Ожидался хотя бы один пробел после 'struct'")

        # NAME_STRUCT
        field_name = read_identifier()

        if field_name is None:
            err("Ожидалось имя структуры")
        elif field_name in TYPES:
            err("Имя не может совпадать с типом данных")
        elif field_name in KEYWORDS:
            err("Имя структуры не может быть ключевым словом")

        # {
        skip_ws()
        if peek() != "{":
            err("Ожидался символ '{'")
        else:
            adv()

        # =======================
        # BODY
        # =======================
        skip_ws()

        while i < n and peek() != "}":

            field_name = read_identifier()

            if field_name is None:
                err("Ожидалось имя поля")
    # восстановление
                while i < n and peek() not in ",}":
                    adv()
                if peek() == ",":
                    adv()
                    skip_ws()
                    continue
                break

            elif field_name in TYPES:
                err("Имя поля не может совпадать с типом данных")
            skip_ws()

            # :
            if peek() != ":":
                err("Ожидался ':' после имени поля")
            else:
                adv()

            skip_ws()

            # TYPE
            if not read_type():
                err("Ожидался корректный тип поля")

            skip_ws()

            # , или }
            if peek() == ",":
                adv()
                skip_ws()
                continue
            elif peek() == "}":
                break
            else:
                err("Ожидалось ',' или '}'")
                while i < n and peek() not in ",}":
                    adv()
                if peek() == ",":
                    adv()
                    skip_ws()
                    continue
                break

        # }
        if peek() == "}":
            adv()
        else:
            err("Ожидался символ '}'")

        skip_ws()

        # ;
        if peek() == ";":
            adv()
        else:
            err("Ожидался символ ';'")

        return errors