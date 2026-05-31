"""Clang / LLVM analysis helpers for laboratory work 7."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class ToolPaths:
    clang: Optional[str] = None
    opt: Optional[str] = None
    dot: Optional[str] = None

    @property
    def ok(self) -> bool:
        return bool(self.clang and self.opt)

    def missing(self) -> List[str]:
        missing = []
        if not self.clang:
            missing.append("clang")
        if not self.opt:
            missing.append("opt")
        if not self.dot:
            missing.append("dot (Graphviz)")
        return missing


@dataclass
class LLVMReport:
    ast: str = ""
    ir_o0: str = ""
    ir_o2: str = ""
    ir_after_opt: str = ""
    struct_analysis: str = ""
    cfg_summary: str = ""
    cfg_dot_paths: Dict[str, str] = field(default_factory=dict)
    cfg_png_paths: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    commands_log: List[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)


def discover_tools() -> ToolPaths:
    clang = shutil.which("clang")
    opt = shutil.which("opt")
    dot = shutil.which("dot")

    if not clang:
        for candidate in (
            r"C:\Program Files\LLVM\bin\clang.exe",
            r"C:\Program Files (x86)\LLVM\bin\clang.exe",
        ):
            if os.path.isfile(candidate):
                clang = candidate
                break

    if not opt:
        for candidate in (
            r"C:\Program Files\LLVM\bin\opt.exe",
            r"C:\Program Files (x86)\LLVM\bin\opt.exe",
        ):
            if os.path.isfile(candidate):
                opt = candidate
                break

    if not dot:
        for candidate in (
            r"C:\Program Files\Graphviz\bin\dot.exe",
            r"C:\Program Files (x86)\Graphviz\bin\dot.exe",
        ):
            if os.path.isfile(candidate):
                dot = candidate
                break

    return ToolPaths(clang=clang, opt=opt, dot=dot)


def _run(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 120) -> Tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


class ClangLLVMAnalyzer:
    def __init__(self, tools: Optional[ToolPaths] = None):
        self.tools = tools or discover_tools()

    def analyze_file(
        self,
        source_path: Path,
        *,
        build_cfg: bool = True,
        cfg_opt_level: str = "O2",
        run_opt_pass: bool = True,
    ) -> LLVMReport:
        report = LLVMReport()
        source_path = Path(source_path).resolve()

        if not source_path.is_file():
            report.errors.append(f"Файл не найден: {source_path}")
            return report

        if not self.tools.ok:
            report.errors.append(
                "Не найдены инструменты: "
                + ", ".join(self.tools.missing())
                + ".\nУстановите LLVM/Clang и Graphviz (см. README, раздел ЛР7)."
            )
            return report

        with tempfile.TemporaryDirectory(prefix="lab7_llvm_") as tmp:
            work = Path(tmp)
            report.ast = self._get_ast(source_path, report)
            report.ir_o0 = self._get_ir(source_path, "O0", report)
            report.ir_o2 = self._get_ir(source_path, "O2", report)

            if run_opt_pass:
                ll_o0 = work / "out_O0.ll"
                ll_o0.write_text(report.ir_o0, encoding="utf-8")
                report.ir_after_opt = self._run_opt_pipeline(ll_o0, report)

            if build_cfg:
                self._build_cfg(source_path, work, cfg_opt_level, report)

        report.struct_analysis = analyze_struct_passing(
            report.ir_o0, report.ir_o2, source_path.name
        )
        return report

    def analyze_source_text(self, source: str, suffix: str = ".c", **kwargs) -> LLVMReport:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=suffix, delete=False, encoding="utf-8"
        ) as f:
            f.write(source)
            path = Path(f.name)
        try:
            return self.analyze_file(path, **kwargs)
        finally:
            path.unlink(missing_ok=True)

    def _log_cmd(self, report: LLVMReport, cmd: List[str]) -> None:
        report.commands_log.append(" ".join(cmd))

    def _get_ast(self, source: Path, report: LLVMReport) -> str:
        cmd = [
            self.tools.clang,
            "-Xclang",
            "-ast-dump",
            "-fsyntax-only",
            "-std=c11",
            str(source),
        ]
        self._log_cmd(report, cmd)
        code, out, err = _run(cmd)
        text = (out + err).strip()
        if code != 0 and not text:
            report.errors.append(f"clang AST: код {code}\n{err}")
        return text or err

    def _get_ir(self, source: Path, opt: str, report: LLVMReport) -> str:
        level = opt.upper().replace("O", "")
        cmd = [
            self.tools.clang,
            f"-O{level}",
            "-S",
            "-emit-llvm",
            "-std=c11",
            str(source),
            "-o",
            "-",
        ]
        self._log_cmd(report, cmd)
        code, out, err = _run(cmd)
        if code != 0:
            report.errors.append(f"clang IR ({opt}): {err.strip() or f'код {code}'}")
            return err.strip()
        return out

    def _run_opt_pipeline(self, ll_path: Path, report: LLVMReport) -> str:
        out_path = ll_path.with_name("opt_O2.ll")
        cmd = [
            self.tools.opt,
            "-passes=default<O2>",
            str(ll_path),
            "-S",
            "-o",
            str(out_path),
        ]
        self._log_cmd(report, cmd)
        code, _, err = _run(cmd, cwd=ll_path.parent)
        if code != 0:
            report.errors.append(f"opt: {err.strip() or f'код {code}'}")
            return ""
        return out_path.read_text(encoding="utf-8", errors="replace")

    def _build_cfg(self, source: Path, work: Path, opt_level: str, report: LLVMReport) -> None:
        level = opt_level.upper().replace("O", "")
        ll_path = work / "cfg.ll"
        cmd_clang = [
            self.tools.clang,
            f"-O{level}",
            "-S",
            "-emit-llvm",
            "-std=c11",
            str(source),
            "-o",
            str(ll_path),
        ]
        self._log_cmd(report, cmd_clang)
        code, _, err = _run(cmd_clang)
        if code != 0:
            report.errors.append(f"CFG IR: {err.strip()}")
            return

        cmd_opt = [
            self.tools.opt,
            "-passes=dot-cfg",
            "-disable-output",
            str(ll_path),
        ]
        self._log_cmd(report, cmd_opt)
        code, _, err = _run(cmd_opt, cwd=work)
        if code != 0:
            report.errors.append(f"opt dot-cfg: {err.strip()}")
            return

        dots = sorted(work.glob("*.dot"))
        if not dots:
            report.cfg_summary = "DOT-файлы CFG не созданы (возможно, функции удалены оптимизацией)."
            return

        lines = ["Сгенерированные CFG (Graphviz DOT):", ""]
        for dot_file in dots:
            name = dot_file.stem.lstrip(".")
            report.cfg_dot_paths[name] = str(dot_file)
            lines.append(f"  • {name}: {dot_file.name}")

            if self.tools.dot:
                png_path = dot_file.with_suffix(".png")
                cmd_dot = [self.tools.dot, "-Tpng", str(dot_file), "-o", str(png_path)]
                self._log_cmd(report, cmd_dot)
                c, _, e = _run(cmd_dot)
                if c == 0:
                    report.cfg_png_paths[name] = str(png_path)
                    lines.append(f"    PNG: {png_path.name}")
                else:
                    lines.append(f"    (PNG не создан: {e.strip()})")

        report.cfg_summary = "\n".join(lines)


def _extract_function_signature(ir: str, func_name: str) -> Optional[str]:
    pattern = re.compile(
        rf"define\s+[\w\s@\"%.]+\s+@{re.escape(func_name)}\s*\([^)]*\)",
        re.MULTILINE,
    )
    m = pattern.search(ir)
    return m.group(0) if m else None


def _extract_call_sites(ir: str, callee: str) -> List[str]:
    return re.findall(rf"call\s+[^@\n]*@{re.escape(callee)}\s*\([^)]*\)", ir)


def analyze_struct_passing(ir_o0: str, ir_o2: str, filename: str = "") -> str:
    """Heuristic report for struct-by-value passing (variant 2.2)."""
    lines: List[str] = [
        "=== Анализ передачи структур (вариант: структуры / записи) ===",
        f"Файл: {filename}" if filename else "",
        "",
    ]

    markers_o0 = {
        "byval": "byval" in ir_o0,
        "sret": "sret" in ir_o0,
        "alloca struct": bool(re.search(r"alloca\s+%struct\.", ir_o0)),
        "memcpy/memmove": "memcpy" in ir_o0 or "memmove" in ir_o0,
        "вызов @sum": "@sum" in ir_o0,
    }
    markers_o2 = {
        "byval": "byval" in ir_o2,
        "sret": "sret" in ir_o2,
        "alloca struct": bool(re.search(r"alloca\s+%struct\.", ir_o2)),
        "memcpy/memmove": "memcpy" in ir_o2 or "memmove" in ir_o2,
        "вызов @sum": "@sum" in ir_o2,
    }

    lines.append("Маркеры в IR -O0:")
    for k, v in markers_o0.items():
        lines.append(f"  • {k}: {'да' if v else 'нет'}")
    lines.append("")
    lines.append("Маркеры в IR -O2:")
    for k, v in markers_o2.items():
        lines.append(f"  • {k}: {'да' if v else 'нет'}")
    lines.append("")

    sig_o0 = _extract_function_signature(ir_o0, "sum")
    sig_o2 = _extract_function_signature(ir_o2, "sum")
    if sig_o0:
        lines.append("Сигнатура @sum (-O0):")
        lines.append(f"  {sig_o0}")
    if sig_o2:
        lines.append("Сигнатура @sum (-O2):")
        lines.append(f"  {sig_o2}")
    elif "@sum" not in ir_o2:
        lines.append("Функция @sum в IR -O2 отсутствует (встраивание / удаление мёртвого кода).")
    lines.append("")

    calls_o0 = _extract_call_sites(ir_o0, "sum")
    calls_o2 = _extract_call_sites(ir_o2, "sum")
    lines.append(f"Вызовы @sum в -O0: {len(calls_o0)}")
    for c in calls_o0[:3]:
        lines.append(f"  {c.strip()}")
    lines.append(f"Вызовы @sum в -O2: {len(calls_o2)}")
    lines.append("")

    lines.append("Вывод:")
    if markers_o0.get("byval"):
        lines.append(
            "  При -O0 передача структуры в IR оформлена как byval — "
            "семантика передачи по значению на уровне ABI (копия аргумента)."
        )
    elif markers_o0.get("alloca struct"):
        lines.append(
            "  При -O0 структура размещается на стеке (alloca), поля читаются load/store — "
            "типичное представление до mem2reg."
        )
    else:
        lines.append(
            "  При -O0 явных byval/alloca не найдено — возможна передача полей в регистрах "
            "(зависит от целевой ABI и размера struct)."
        )

    if not markers_o2.get("вызов @sum") and "@sum" not in ir_o2:
        lines.append(
            "  При -O2 вызов sum исчез: константы {2,3} свёрнуты, функция встроена; "
            "передача структуры как отдельного аргумента не нужна."
        )
    elif markers_o2.get("byval") and markers_o2.get("вызов @sum"):
        lines.append(
            "  При -O2 вызов сохранён; byval указывает на передачу по значению в IR/ABI."
        )
    else:
        lines.append(
            "  При -O2 IR упрощён: меньше alloca/load/store, возможна SSA-форма и скаляризация."
        )

    if "alwaysinline" in ir_o0 or "alwaysinline" in ir_o2:
        lines.append(
            "  Обнаружен атрибут alwaysinline — компилятор обязан попытаться встроить функцию."
        )

    lines.append("")
    lines.append(
        "Итог: в исходном C struct передаётся по значению; LLVM отражает это через byval/копию "
        "или разложение на регистры; при -O2 для константного примера оптимизатор устраняет "
        "передачу целиком."
    )
    return "\n".join(lines)


def format_report(report: LLVMReport) -> str:
    parts = []
    if report.errors:
        parts.append("=== Ошибки ===\n" + "\n".join(report.errors) + "\n")

    if report.commands_log:
        parts.append("=== Выполненные команды ===\n" + "\n".join(report.commands_log) + "\n")

    parts.append("=== AST (clang -ast-dump) ===\n" + (report.ast or "(пусто)") + "\n")
    parts.append("=== LLVM IR (-O0) ===\n" + (report.ir_o0 or "(пусто)") + "\n")
    parts.append("=== LLVM IR (-O2) ===\n" + (report.ir_o2 or "(пусто)") + "\n")

    if report.ir_after_opt:
        parts.append("=== LLVM IR (opt -passes=default<O2>) ===\n" + report.ir_after_opt + "\n")

    if report.struct_analysis:
        parts.append(report.struct_analysis + "\n")

    if report.cfg_summary:
        parts.append("=== CFG ===\n" + report.cfg_summary + "\n")

    return "\n".join(parts)


def is_c_source(text: str, filename: Optional[str] = None) -> bool:
    if filename:
        low = filename.lower()
        if low.endswith((".c", ".cpp", ".cc", ".cxx", ".h", ".hpp")):
            return True
    hints = ("#include", "struct ", "int main", "printf(", "__attribute__")
    return sum(1 for h in hints if h in text) >= 2
