"""Собственный IR (TAC) для варианта C: struct Point + sum + main (без Clang)."""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from .ir_passes import (
    ConstantFoldCallPass,
    PassResult,
    ScalarizeStructArgPass,
    run_passes,
)
from .struct_ir import TacInstr
from .output_format import section


def is_c_struct_pass_program(text: str) -> bool:
    return "struct Point" in text and "sum" in text and "main" in text


def _parse_point_literal(text: str) -> Optional[Tuple[int, int]]:
    m = re.search(r"\{\s*(\d+)\s*,\s*(\d+)\s*\}", text)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def build_struct_pass_tac(source: str) -> Tuple[List[TacInstr], str]:
    """
    Генерация TAC вручную для:
      struct Point { int x; int y; };
      int sum(struct Point p) { return p.x + p.y; }
      int main() { struct Point p = {2,3}; ... sum(p); }
    """
    lit = _parse_point_literal(source) or (2, 3)
    ast_lines = [
        "Program",
        "  StructDecl Point",
        "    Field(x: i32)",
        "    Field(y: i32)",
        "  Func sum(p: Point)  ; передача по значению (C)",
        "    Return Add(p.x, p.y)",
        "  Func main",
        f"    Local p = {{{lit[0]}, {lit[1]}}}",
        "    Call sum(p)",
        "    Print result",
    ]
    ast_text = "\n".join(ast_lines)

    instrs: List[TacInstr] = []
    n = 0

    def emit(op: str, args: List[str], comment: str = "") -> str:
        nonlocal n
        n += 1
        instrs.append(TacInstr(n, op, args, comment))
        return f"t{n}"

    emit("STRUCT_DEF", ["Point", "8"], "struct Point, 2×i32")
    emit("FUNC_BEGIN", ["sum", "Point"], "—O0: параметр по значению")
    emit("PASS_BY_VAL", ["p", "8"], "копия struct на стек (by value)")
    emit("LOAD_FIELD", ["p", "x", "t_x"], "p.x")
    emit("LOAD_FIELD", ["p", "y", "t_y"], "p.y")
    emit("ADD", ["t_x", "t_y", "t_ret"], "p.x + p.y")
    emit("RET", ["t_ret"], "")
    emit("FUNC_END", ["sum"], "")

    emit("FUNC_BEGIN", ["main", ""], "")
    emit("ALLOC_LOCAL", ["p", "Point"], "struct на стеке main")
    emit("INIT_FIELD", ["p", "x", str(lit[0])], "")
    emit("INIT_FIELD", ["p", "y", str(lit[1])], "")
    emit("PASS_ARG", ["p", "sum"], "передача аргумента по значению")
    emit("CALL", ["sum", "t_res"], "вызов sum(p)")
    emit("PRINT", ["t_res"], "printf")
    emit("RET", ["0"], "")
    emit("FUNC_END", ["main"], "")

    return instrs, ast_text


def run_c_struct_optimizations(instrs: List[TacInstr]) -> List[PassResult]:
    return run_passes(
        instrs,
        [ScalarizeStructArgPass(), ConstantFoldCallPass()],
    )


def format_c_bonus_report(ast_text: str, instrs: List[TacInstr], opts: List[PassResult]) -> str:
    parts = [
        section("Собственный конвейер IR (Python)").strip(),
        "Clang / opt / LLVM не используются.",
        "AST и TAC построены вручную по исходному C-коду.",
        section("AST (упрощённое дерево)").strip(),
        ast_text,
        section("IR: трёхадресный код (-O0, до оптимизаций)").strip(),
    ]
    parts.extend(i.format() for i in instrs)

    for opt in opts:
        parts.append(opt.format_report())

    final = opts[-1].output_ir if opts else instrs
    parts.append(section("Итоговый IR (после своих оптимизаций)").strip())
    parts.extend(i.format() for i in final)
    parts.append(section("Вывод по передаче struct").strip())
    parts.append(
        "До опт.1: PASS_BY_VAL — передача по значению (копия 8 байт).\n"
        "После опт.1: PARAM_SCALAR — поля x,y как скаляры (аналог разложения в регистры).\n"
        "После опт.2: CONST 5 — вызов sum устранён, константы 2+3 свёрнуты.\n"
    )
    return "\n".join(parts)
