"""TAC для объявления struct (Rust) и запуск собственных оптимизаций (без Clang)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .struct_ast import StructDeclNode, TYPE_SIZES, FieldNode
from .ir_passes import (
    CanonicalFieldOrderPass,
    ConstantFoldLayoutPass,
    PassResult,
    run_passes,
)
from .output_format import section


@dataclass
class TacInstr:
    index: int
    op: str
    args: List[str]
    comment: str = ""

    def format(self) -> str:
        args_s = ", ".join(self.args) if self.args else ""
        c = f"  ; {self.comment}" if self.comment else ""
        return f"{self.index:3d}: {self.op}({args_s}){c}"


def ast_to_tac(node: StructDeclNode) -> List[TacInstr]:
    """Генератор TAC: объявление struct → виртуальные инструкции."""
    instrs: List[TacInstr] = []
    n = 0

    def emit(op: str, args: List[str], comment: str = "") -> str:
        nonlocal n
        n += 1
        instrs.append(TacInstr(n, op, args, comment))
        return f"t{n}"

    pub_arg = "true" if node.is_pub else "false"
    emit("STRUCT_BEGIN", [node.name, pub_arg], "начало объявления")

    offset_temp = None
    for fld in node.fields:
        emit("FIELD_DECL", [node.name, fld.name, fld.type_name], f"поле {fld.name}")
        width = TYPE_SIZES.get(fld.type_name, 0)
        wtemp = emit("TYPE_WIDTH", [fld.type_name, str(width)], "ширина типа")
        if offset_temp is None:
            offset_temp = emit("FIELD_OFFSET", [fld.name, "0"], "смещение 0")
        else:
            offset_temp = emit("ADD_OFFSET", [offset_temp, wtemp], "смещение += width")

    if node.fields:
        last_w = TYPE_SIZES.get(node.fields[-1].type_name, 0)
        total_lhs = emit("ADD", [offset_temp or "0", str(last_w)], "размер (несвёрнутый)")
        emit("TOTAL_SIZE", [total_lhs], "до const fold")
    else:
        emit("TOTAL_SIZE", ["0"], "пустая struct")

    emit("STRUCT_END", [node.name], "конец")
    return instrs


def tac_to_canonical_string(instrs: List[TacInstr]) -> str:
    parts = []
    for ins in instrs:
        if ins.op == "STRUCT_BEGIN":
            parts.append(f"struct {ins.args[0]}" + (" [pub]" if ins.args[1] == "true" else "") + " {")
        elif ins.op == "FIELD_DECL":
            parts.append(f"  {ins.args[1]} : {ins.args[2]}")
        elif ins.op == "STRUCT_END":
            parts.append("};")
        elif ins.op == "TOTAL_SIZE":
            parts.append(f"/* size: {ins.args[0]} */")
        elif ins.op == "STRUCT_DEF":
            parts.append(f"struct {ins.args[0]} {{ /* {ins.args[1]} bytes */ }}")
        elif ins.op == "PARAM_SCALAR":
            parts.append(f"  param {ins.args[1]}: {ins.args[2]}")
        elif ins.op == "CONST":
            parts.append(f"  const result: {ins.args[0]}")
    return "\n".join(parts)


def run_optimizations(instrs: List[TacInstr]) -> List[PassResult]:
    """Две локальные оптимизации — только Python (ir_passes.py)."""
    return run_passes(
        instrs,
        [CanonicalFieldOrderPass(), ConstantFoldLayoutPass()],
    )


def format_full_bonus_report(
    ast_text: str,
    instrs: List[TacInstr],
    opts: List[PassResult],
) -> str:
    parts = [
        section("Собственный конвейер IR (Python)").strip(),
        "Clang / opt / LLVM не используются.",
        section("AST (объявление struct, ЛР5)").strip(),
        ast_text,
        section("IR: трёхадресный код (до оптимизаций)").strip(),
    ]
    parts.extend(i.format() for i in instrs)
    parts.append(section("Каноническая строковая форма").strip())
    parts.append(tac_to_canonical_string(instrs))

    for opt in opts:
        parts.append(opt.format_report())

    final = opts[-1].output_ir if opts else instrs
    parts.append(section("Итоговый IR (после своих оптимизаций)").strip())
    parts.extend(i.format() for i in final)
    parts.append(section("Каноническая форма (итог)").strip())
    parts.append(tac_to_canonical_string(final))

    return "\n".join(parts)
