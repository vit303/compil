"""Локальные оптимизации IR — собственная реализация на Python (без Clang/opt)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# TacInstr определён в struct_ir; импорт внизу в run_* во избежание циклов


def _tac():
    from .struct_ir import TacInstr
    return TacInstr


def clone_ir(instrs: List["TacInstr"]) -> List["TacInstr"]:
    TacInstr = _tac()
    return [TacInstr(t.index, t.op, list(t.args), t.comment) for t in instrs]


def reindex_ir(instrs: List["TacInstr"]) -> List["TacInstr"]:
    TacInstr = _tac()
    return [TacInstr(i + 1, t.op, list(t.args), t.comment) for i, t in enumerate(instrs)]


@dataclass
class PassResult:
    name: str
    title: str
    description: str
    input_ir: List
    output_ir: List
    steps: List[str] = field(default_factory=list)

    def format_report(self) -> str:
        lines = [
            self.title,
            self.description,
            "(реализация: Python, Clang/opt не используются)",
            "",
            "Шаги алгоритма",
            "",
        ]
        lines.extend(f"  {i + 1}. {s}" for i, s in enumerate(self.steps))
        lines.extend(["", "Входной IR", ""])
        lines.extend(t.format() for t in self.input_ir)
        lines.append("")
        lines.append("Выходной IR")
        lines.append("")
        lines.extend(t.format() for t in self.output_ir)
        lines.append("")
        return "\n".join(lines)


class LocalOptimizationPass(ABC):
    name: str = "pass"
    title: str = "Pass"
    description: str = ""

    @abstractmethod
    def apply(self, instrs: List) -> Tuple[List, List[str]]:
        """Преобразовать IR; вернуть (новый IR, журнал шагов)."""


class CanonicalFieldOrderPass(LocalOptimizationPass):
    """Опт. 1 (Rust struct): упорядочить FIELD_DECL по имени, пересчитать смещения."""

    name = "canonical_field_order"
    title = "Оптимизация 1: канонический порядок полей"
    description = (
        "Локальная канонизация внутри одного объявления struct: "
        "инструкции FIELD_DECL переставляются по алфавиту имён полей, "
        "затем заново генерируются OFFSET/TOTAL_SIZE."
    )

    def apply(self, instrs: List) -> Tuple[List, List[str]]:
        steps: List[str] = []
        struct_name, is_pub = "", "false"
        fields: List[Tuple[str, str]] = []

        for ins in instrs:
            if ins.op == "STRUCT_BEGIN":
                struct_name, is_pub = ins.args[0], ins.args[1]
            elif ins.op == "FIELD_DECL":
                fields.append((ins.args[1], ins.args[2]))

        steps.append(f"Считано полей: {len(fields)} → {fields}")
        ordered = sorted(fields, key=lambda x: x[0].lower())
        steps.append(f"Сортировка по имени: {ordered}")

        from .struct_ast import FieldNode, StructDeclNode
        from .struct_ir import ast_to_tac

        node = StructDeclNode(
            name=struct_name,
            fields=[FieldNode(n, t, 0, 0) for n, t in ordered],
            is_pub=(is_pub == "true"),
        )
        out = ast_to_tac(node)
        for ins in out:
            if ins.op == "FIELD_DECL":
                ins.comment = "канонический порядок"
        steps.append("Пересобран TAC с новым порядком полей")
        return out, steps


class ConstantFoldLayoutPass(LocalOptimizationPass):
    """Опт. 2 (Rust struct): свёртка TYPE_WIDTH / ADD / TOTAL_SIZE."""

    name = "const_fold_layout"
    title = "Оптимизация 2: свёртка констант (размер struct)"
    description = (
        "Локальная свёртка: для каждого поля известна константа TYPE_WIDTH; "
        "цепочка ADD заменяется одной константой в TOTAL_SIZE."
    )

    def apply(self, instrs: List) -> Tuple[List, List[str]]:
        from .struct_ast import TYPE_SIZES

        TacInstr = _tac()
        steps: List[str] = []
        widths: List[int] = []
        temps: Dict[str, int] = {}

        for ins in instrs:
            if ins.op == "FIELD_DECL":
                w = TYPE_SIZES.get(ins.args[2], 0)
                widths.append(w)
                steps.append(f"FIELD {ins.args[1]}:{ins.args[2]} → width={w}")
            elif ins.op == "TYPE_WIDTH" and len(ins.args) >= 2:
                temps[f"t{ins.index}"] = int(ins.args[1])
            elif ins.op == "ADD" and len(ins.args) >= 2:
                left = temps.get(ins.args[0], 0)
                try:
                    right = int(ins.args[1])
                except ValueError:
                    right = 0
                val = left + right
                temps[f"t{ins.index}"] = val
                steps.append(f"Свёртка {ins.args[0]}+{ins.args[1]} → {val}")

        total = sum(widths)
        steps.append(f"Итог TOTAL_SIZE: {' + '.join(map(str, widths))} → {total}")

        out: List[TacInstr] = []
        n = 0
        skip_ops = {"TYPE_WIDTH", "ADD_OFFSET", "ADD", "FIELD_OFFSET"}

        def emit(op: str, args: List[str], comment: str = "") -> None:
            nonlocal n
            n += 1
            out.append(TacInstr(n, op, args, comment))

        for ins in instrs:
            if ins.op in skip_ops:
                continue
            if ins.op == "TOTAL_SIZE":
                emit("TOTAL_SIZE", [str(total)], f"const fold: {total}")
            elif ins.op == "FIELD_DECL":
                w = TYPE_SIZES.get(ins.args[2], 0)
                emit(ins.op, ins.args, f"width: {w}")
            else:
                emit(ins.op, ins.args, ins.comment)

        return out, steps


class ScalarizeStructArgPass(LocalOptimizationPass):
    """Опт. 1 (C): передача struct по значению → скаляры в регистрах."""

    name = "scalarize_struct_arg"
    title = "Оптимизация 1: скаляризация передачи struct"
    description = (
        "Локально в функции sum: вместо копирования struct целиком (PASS_BY_VAL) "
        "параметры разбиваются на скалярные i32."
    )

    def apply(self, instrs: List) -> Tuple[List, List[str]]:
        TacInstr = _tac()
        steps = ["Найти PASS_BY_VAL → заменить на PARAM_SCALAR"]
        out: List = []
        n = 0

        def emit(op: str, args: List[str], comment: str = "") -> None:
            nonlocal n
            n += 1
            out.append(TacInstr(n, op, args, comment))

        for ins in instrs:
            if ins.op == "PASS_BY_VAL":
                steps.append(f"Удалено: {ins.format().strip()}")
                emit("PARAM_SCALAR", [ins.args[0], "x", "i32"], "поле x в регистре")
                emit("PARAM_SCALAR", [ins.args[0], "y", "i32"], "поле y в регистре")
            elif ins.op in ("LOAD_FIELD", "COPY_STRUCT"):
                steps.append(f"Удалено (не нужно после скаляризации): {ins.op}")
            elif ins.op == "ADD" and ins.args[:2] == ["t_x", "t_y"]:
                emit("ADD", ["x", "y", "result"], "сложение скаляров")
                steps.append("ADD t_x,t_y заменён на ADD x,y,result")
            else:
                emit(ins.op, ins.args, ins.comment)

        steps.append("IR упрощён: нет копирования struct на стеке")
        return out, steps


class ConstantFoldCallPass(LocalOptimizationPass):
    """Опт. 2 (C): свёртка констант {2,3} и устранение вызова sum."""

    name = "const_fold_call"
    title = "Оптимизация 2: свёртка констант и устранение вызова"
    description = (
        "Локально в main: литерал {2,3} сворачивается в 5, "
        "вызов sum удаляется (const fold + DCE в пределах main)."
    )

    def apply(self, instrs: List) -> Tuple[List, List[str]]:
        TacInstr = _tac()
        steps: List[str] = []
        out: List = []
        n = 0
        fold_x, fold_y = None, None
        in_main = False

        def emit(op: str, args: List[str], comment: str = "") -> None:
            nonlocal n
            n += 1
            out.append(TacInstr(n, op, args, comment))

        for ins in instrs:
            if ins.op == "FUNC_BEGIN" and ins.args and ins.args[0] == "main":
                in_main = True
            elif ins.op == "FUNC_END" and ins.args and ins.args[0] == "main":
                in_main = False

            if ins.op == "INIT_FIELD" and len(ins.args) >= 3:
                if ins.args[1] == "x":
                    fold_x = int(ins.args[2])
                elif ins.args[1] == "y":
                    fold_y = int(ins.args[2])
                steps.append(f"Запомнена константа {ins.args[1]}: {ins.args[2]}")
                continue
            if ins.op == "CALL" and ins.args and ins.args[0] == "sum":
                if fold_x is not None and fold_y is not None:
                    total = fold_x + fold_y
                    steps.append(f"Свёртка: sum({fold_x},{fold_y}) → {total}")
                    emit("CONST", [str(total), "result"], f"const fold {fold_x}+{fold_y}")
                    continue
            if in_main and ins.op in (
                "PASS_ARG", "ALLOC_LOCAL", "INIT_FIELD", "CALL",
            ):
                if ins.op == "CALL":
                    continue
                steps.append(f"Удалено в main после свёртки: {ins.op}")
                continue
            emit(ins.op, ins.args, ins.comment)

        return out, steps


def run_passes(instrs: List, passes: List[LocalOptimizationPass]) -> List[PassResult]:
    results: List[PassResult] = []
    current = instrs
    for p in passes:
        inp = clone_ir(current)
        out, steps = p.apply(current)
        out = reindex_ir(out)
        results.append(
            PassResult(
                name=p.name,
                title=p.title,
                description=p.description,
                input_ir=inp,
                output_ir=out,
                steps=steps,
            )
        )
        current = out
    return results
