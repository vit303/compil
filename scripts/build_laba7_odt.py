#!/usr/bin/env python3
"""Сборка ЛАБА7.odt из текста и скриншотов screenshots/photo_1-5.jpg"""

from pathlib import Path

from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties, GraphicProperties
from odf.text import H, P, Span
from odf.draw import Frame, Image

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS = ROOT / "screenshots"
OUT = ROOT / "ЛАБА7.odt"


def add_heading(doc, text: str, level: int = 1) -> None:
    h = H(outlinelevel=level, text=text)
    doc.text.addElement(h)


def add_para(doc, text: str) -> None:
    doc.text.addElement(P(text=text))


def add_image(doc, path: Path, caption: str) -> None:
    if not path.is_file():
        add_para(doc, f"[Нет файла: {path.name}]")
        return
    href = path.name
    photostyle = Style(name="Fr1", family="graphic")
    photostyle.addElement(
        GraphicProperties(
            stroke="none",
            fill="none",
            wrap="dynamic",
            numberwrappedparagraphs="no-limit",
            verticalpos="top",
            verticalrel="paragraph",
            horizontalpos="center",
            horizontalrel="paragraph",
        )
    )
    doc.automaticstyles.addElement(photostyle)
    p = P()
    frame = Frame(
        width="17cm",
        height="10cm",
        anchortype="paragraph",
        stylename=photostyle,
    )
    img = Image(href=href)
    frame.addElement(img)
    p.addElement(frame)
    doc.addPicture(path)
    doc.text.addElement(p)
    add_para(doc, caption)


def build() -> None:
    doc = OpenDocumentText()

    add_heading(doc, "Лабораторная работа 7", 1)
    add_heading(doc, "Анализ и преобразование кода (собственный IR и оптимизации)", 2)

    add_para(
        doc,
        "Автор: Зоркольцев Илья Алексеевич\n"
        "Группа: АВТ-313\n"
        "Год: 2026",
    )

    add_heading(doc, "Цель работы", 2)
    add_para(
        doc,
        "Познакомиться с построением AST и промежуточного представления (TAC), "
        "применить локальные оптимизации, проанализировать передачу структур в C "
        "и интегрировать все этапы в GUI языкового процессора (продолжение ЛР 1–5).",
    )

    add_heading(doc, "Постановка задачи", 2)
    add_para(doc, "Общее задание:")
    for item in [
        "Построить AST для программы на C/C++.",
        "Сгенерировать промежуточное представление (TAC).",
        "Применить оптимизации IR.",
        "Проанализировать результат.",
    ]:
        add_para(doc, f"• {item}")

    add_para(doc, "Индивидуальный вариант 2.2 — структуры / записи:")
    add_para(
        doc,
        "Исследовать передачу struct Point в функцию sum; сравнить IR до и после оптимизаций.",
    )

    add_heading(doc, "Используемые технологии", 2)
    add_para(doc, "Python 3, PyQt6, собственные модули app/struct_ast.py, app/struct_ir.py, app/ir_passes.py, app/c_struct_ir.py.")

    add_heading(doc, "Запуск", 2)
    add_para(doc, "pip install -r requirements.txt")
    add_para(doc, "python main.py")

    add_heading(doc, "Общая часть", 2)
    add_para(
        doc,
        "Пример main.c (функции square и main) находится в examples/lab7/main.c. "
        "Для варианта struct используется examples/lab7/struct_pass.c.",
    )

    add_heading(doc, "Дополнительное задание: AST, TAC и две локальные оптимизации", 2)
    add_para(
        doc,
        "Конструкция из КР/ЛР5: объявление struct на языке Rust. "
        "Clang и LLVM не используются — реализация на Python.",
    )

    add_para(doc, "Тестовый пример:")
    add_para(
        doc,
        "struct Product {\n"
        "    price: f64,\n"
        "    id: u64,\n"
        "    name: String\n"
        "};",
    )

    captions = [
        ("photo_1.jpg", "Рис. 1. GUI: исходный код и вкладка «КР: AST / TAC» — AST и IR до оптимизаций."),
        ("photo_2.jpg", "Рис. 2. Оптимизация 1: канонический порядок полей — входной IR."),
        ("photo_3.jpg", "Рис. 3. Оптимизация 1: выходной IR после упорядочивания полей."),
        ("photo_4.jpg", "Рис. 4. Оптимизация 2: свёртка констант размера struct — входной и выходной IR."),
        ("photo_5.jpg", "Рис. 5. Итоговый IR и каноническая форма после обеих оптимизаций."),
    ]
    for name, cap in captions:
        add_image(doc, SCREENSHOTS / name, cap)

    add_heading(doc, "Оптимизация 1: канонический порядок полей", 2)
    add_para(
        doc,
        "Локальная канонизация: поля struct сортируются по имени, TAC перестраивается. "
        "Семантика типов полей сохраняется.",
    )

    add_heading(doc, "Оптимизация 2: свёртка констант (размер struct)", 2)
    add_para(
        doc,
        "Локальная свёртка: суммируются TYPE_WIDTH полей, цепочка ADD заменяется константой TOTAL_SIZE(40).",
    )

    add_heading(doc, "Индивидуальное задание: передача struct (C)", 2)
    add_para(
        doc,
        "Для struct_pass.c собственный TAC отражает PASS_BY_VAL (передача по значению). "
        "Оптимизация 1 — скаляризация параметра; оптимизация 2 — свёртка sum(2,3) в константу 5.",
    )

    add_heading(doc, "Выводы", 2)
    add_para(
        doc,
        "1. AST и TAC позволяют формально описать синтаксическую конструкцию.\n"
        "2. Локальные оптимизации упрощают IR без изменения семантики.\n"
        "3. Передача struct в C по значению в TAC выражается копированием; "
        "после оптимизаций вызов может быть устранён при константных аргументах.\n"
        "4. GUI обеспечивает наглядный вывод входного и выходного IR для каждой оптимизации.",
    )

    add_heading(doc, "Контрольные вопросы (кратко)", 2)
    qa = [
        ("Clang", "фронтенд компилятора: парсинг, AST, генерация IR."),
        ("LLVM", "инфраструктура оптимизации и генерации машинного кода."),
        ("AST vs IR", "AST — структура исходника; IR — низкоуровневые инструкции."),
        ("Зачем IR", "единое представление для оптимизаций и переносимости."),
        ("alloca", "выделение памяти на стеке в LLVM IR."),
        ("SSA", "каждое значение присваивается один раз — удобно для анализа."),
        ("CFG", "граф базовых блоков и переходов функции."),
    ]
    for q, a in qa:
        add_para(doc, f"{q}: {a}")

    doc.save(str(OUT))
    print(f"Written: {OUT}")


if __name__ == "__main__":
    build()
