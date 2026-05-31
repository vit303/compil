#!/usr/bin/env python3
"""Генерация блок-схем для ЛР7: photo_9.jpg, photo_10.jpg"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "screenshots"


def draw_box(ax, x, y, w, h, text, kind="process"):
    if kind == "terminal":
        boxstyle = "round,pad=0.02,rounding_size=0.8"
        fc, ec = "#e8f4e8", "#2d6a2d"
    elif kind == "decision":
        boxstyle = "round,pad=0.02,rounding_size=0.15"
        fc, ec = "#fff4e6", "#b45309"
    else:
        boxstyle = "round,pad=0.02,rounding_size=0.1"
        fc, ec = "#e8f0fe", "#1d4ed8"

    rect = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle=boxstyle,
        linewidth=1.5,
        facecolor=fc,
        edgecolor=ec,
    )
    ax.add_patch(rect)
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=9,
        wrap=True,
        family="DejaVu Sans",
    )


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.2,
            color="#374151",
        )
    )


def flowchart_opt1():
    fig, ax = plt.subplots(figsize=(8, 11), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis("off")

    xs, w, h = 5, 4.2, 0.55
    y = 13.2
    draw_box(ax, xs, y, w, h, "Начало", "terminal")
    y -= 1.0
    arrow(ax, xs, y + 0.35, xs, y - 0.25)

    steps = [
        ("Входной IR\n(список инструкций TAC)", "process"),
        ("struct_name := \"\"\nfields := []", "process"),
        ("Для каждой инструкции ins", "process"),
        ("ins.op == STRUCT_BEGIN?", "decision"),
        ("Сохранить имя struct\nи флаг pub", "process"),
        ("ins.op == FIELD_DECL?", "decision"),
        ("Добавить (имя, тип)\nв fields", "process"),
        ("fields := sort(fields,\nпо имени поля)", "process"),
        ("Собрать StructDeclNode\nиз struct_name и fields", "process"),
        ("out := ast_to_tac(node)\nпересчёт OFFSET / TOTAL_SIZE", "process"),
        ("Выходной IR", "process"),
        ("Конец", "terminal"),
    ]

    for text, kind in steps:
        y -= 0.95 if kind != "terminal" else 0.85
        draw_box(ax, xs, y, w, h if "\n" not in text else 0.7, text, kind)
        if kind != "terminal":
            arrow(ax, xs, y + 0.4, xs, y - 0.45)

    ax.set_title(
        "Оптимизация 1: канонический порядок полей\n(CanonicalFieldOrderPass)",
        fontsize=11,
        fontweight="bold",
        pad=12,
    )
    fig.tight_layout()
    fig.savefig(OUT / "photo_9.jpg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def flowchart_opt2():
    fig, ax = plt.subplots(figsize=(8, 12), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 15)
    ax.axis("off")

    xs, w, h = 5, 4.4, 0.55
    y = 14.2
    draw_box(ax, xs, y, w, h, "Начало", "terminal")
    y -= 1.0
    arrow(ax, xs, y + 0.35, xs, y - 0.25)

    steps = [
        ("Входной IR\nwidths := [], temps := {}", "process"),
        ("Проход 1: для каждой ins", "process"),
        ("FIELD_DECL?", "decision"),
        ("width += TYPE_SIZES[тип]", "process"),
        ("TYPE_WIDTH / ADD?", "decision"),
        ("Свёртка констант\nв temps", "process"),
        ("total := sum(widths)", "process"),
        ("Проход 2: для каждой ins", "process"),
        ("op in {TYPE_WIDTH,\nADD_OFFSET, ADD, ...}?", "decision"),
        ("Пропустить инструкцию", "process"),
        ("TOTAL_SIZE?", "decision"),
        ("emit TOTAL_SIZE(total)\nconst fold", "process"),
        ("Иначе: emit ins\n(FIELD_DECL, STRUCT_*)", "process"),
        ("Выходной IR", "process"),
        ("Конец", "terminal"),
    ]

    for text, kind in steps:
        y -= 0.92 if kind != "terminal" else 0.85
        draw_box(ax, xs, y, w, h if text.count("\n") < 2 else 0.72, text, kind)
        if kind != "terminal":
            arrow(ax, xs, y + 0.38, xs, y - 0.42)

    ax.set_title(
        "Оптимизация 2: свёртка констант (размер struct)\n(ConstantFoldLayoutPass)",
        fontsize=11,
        fontweight="bold",
        pad=12,
    )
    fig.tight_layout()
    fig.savefig(OUT / "photo_10.jpg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    flowchart_opt1()
    flowchart_opt2()
    print(f"Saved: {OUT / 'photo_9.jpg'}")
    print(f"Saved: {OUT / 'photo_10.jpg'}")


if __name__ == "__main__":
    main()
