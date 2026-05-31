"""AST для объявления struct (ЛР5 / доп. задание ЛР7)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class FieldNode:
    name: str
    type_name: str
    line: int
    col: int


@dataclass
class StructDeclNode:
    name: str
    fields: List[FieldNode]
    is_pub: bool = False
    line: int = 1
    col: int = 1


@dataclass
class ParseError:
    line: int
    col: int
    message: str
    fragment: str = ""


VALID_TYPES = {
    "bool", "char", "str", "String",
    "i8", "i16", "i32", "i64", "i128", "isize",
    "u8", "u16", "u32", "u64", "u128", "usize",
    "f32", "f64",
}

TYPE_SIZES = {
    "bool": 1, "char": 1, "str": 8, "String": 24,
    "i8": 1, "i16": 2, "i32": 4, "i64": 8, "i128": 16, "isize": 8,
    "u8": 1, "u16": 2, "u32": 4, "u64": 8, "u128": 16, "usize": 8,
    "f32": 4, "f64": 8,
}


class StructASTParser:
    """Строит AST объявления struct (без изменения SyntaxAnalyzer)."""

    def __init__(self):
        self.errors: List[ParseError] = []

    def parse(self, text: str) -> Tuple[Optional[StructDeclNode], List[ParseError]]:
        self.errors = []
        s = text
        n = len(s)
        i = 0
        line = 1
        col = 1

        def peek() -> str:
            return s[i] if i < n else ""

        def adv() -> None:
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

        def err(msg: str, frag: Optional[str] = None) -> None:
            self.errors.append(
                ParseError(line, col, msg, frag if frag is not None else (peek() or "<EOF>"))
            )

        def skip_ws() -> None:
            while i < n and s[i] in " \t\n\r":
                adv()

        def read_ident() -> Optional[str]:
            nonlocal i
            start = i
            if i >= n:
                return None
            ch = peek()
            if not (ch.isalpha() or ch == "_" or (ch == "'" and i + 1 < n and s[i + 1].isalpha())):
                return None
            adv()
            allowed = set("_'@%?*!#^&()-")
            while i < n:
                c = peek()
                if c.isalnum() or c == "_":
                    adv()
                    continue
                if c in allowed:
                    if c == "#" and i + 1 < n and s[i + 1] == "[":
                        break
                    adv()
                    continue
                break
            return s[start:i]

        skip_ws()
        decl_line, decl_col = line, col
        is_pub = False
        word = read_ident()
        if word == "pub":
            is_pub = True
            skip_ws()
            word = read_ident()

        if word != "struct":
            err("Ожидалось 'struct' или 'pub struct'", word or "<EOF>")
            return None, self.errors

        skip_ws()
        struct_name = read_ident()
        if not struct_name:
            err("Ожидалось имя структуры")
            return None, self.errors

        skip_ws()
        if peek() != "{":
            err("Ожидался '{'", peek())
            return None, self.errors
        adv()

        fields: List[FieldNode] = []
        skip_ws()

        while i < n and peek() not in "};":
            skip_ws()
            if peek() in "};":
                break

            fl, fc = line, col
            fname = read_ident()
            if not fname:
                if peek() in "};":
                    break
                while i < n and peek() not in ",};\n":
                    adv()
                if peek() == ",":
                    adv()
                skip_ws()
                continue

            skip_ws()
            if peek() == ":":
                adv()
            skip_ws()

            tl, tc = line, col
            type_name = read_ident()
            if not type_name:
                err("Ожидался тип поля")
            elif type_name not in VALID_TYPES:
                err(f"Неизвестный тип '{type_name}'", type_name)
            else:
                fields.append(FieldNode(fname, type_name, fl, fc))

            skip_ws()
            if peek() == ",":
                adv()
                skip_ws()
            elif peek() == "}":
                break

        skip_ws()
        if peek() == "}":
            adv()
        else:
            err("Ожидался '}'", peek())

        skip_ws()
        if peek() == ";":
            adv()
        else:
            err("Ожидался ';'")

        node = StructDeclNode(
            name=struct_name,
            fields=fields,
            is_pub=is_pub,
            line=decl_line,
            col=decl_col,
        )
        return node, self.errors


def format_ast(node: StructDeclNode, indent: int = 0) -> str:
    pad = "  " * indent
    lines = [
        f"{pad}StructDecl",
        f"{pad}  name: {node.name!r}",
        f"{pad}  pub: {node.is_pub}",
        f"{pad}  fields:",
    ]
    for f in node.fields:
        lines.append(f"{pad}    Field({f.name!r} : {f.type_name!r} @ {f.line}:{f.col})")
    return "\n".join(lines)
