#!/usr/bin/env python3
"""比较同批中文稿件的段落形状，提醒批量套用同一骨架。"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DraftShape:
    path: Path
    han: int
    paragraphs: tuple[int, ...]
    h2: int

    @property
    def paragraph_count(self) -> int:
        return len(self.paragraphs)

    @property
    def paragraph_cv(self) -> float:
        if len(self.paragraphs) < 2:
            return 0.0
        mean = sum(self.paragraphs) / len(self.paragraphs)
        if mean == 0:
            return 0.0
        variance = sum((value - mean) ** 2 for value in self.paragraphs) / len(
            self.paragraphs
        )
        return (variance**0.5) / mean


def han_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def mask_non_prose(text: str) -> str:
    def mask(match: re.Match[str]) -> str:
        return "".join("\n" if char == "\n" else " " for char in match.group())

    patterns = (
        re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", re.DOTALL),
        re.compile(r"```.*?```", re.DOTALL),
        re.compile(r"`[^`\n]*`"),
        re.compile(r"\]\([^\n)]*\)"),
        re.compile(r"https?://[^\s)>]+"),
    )
    masked = text
    for pattern in patterns:
        masked = pattern.sub(mask, masked)
    return masked


def paragraph_lengths(text: str) -> tuple[int, ...]:
    values: list[int] = []
    for block in re.split(r"\n\s*\n", text):
        clean = re.sub(r"[>*_`]", "", block).strip()
        if not clean or clean.startswith(("#", "http", "![", "```")):
            continue
        if re.match(r"^(?:[-+*]|\d+[.、])\s", clean):
            continue
        count = han_count(clean)
        if count >= 4:
            values.append(count)
    return tuple(values)


def read_shape(path: Path) -> DraftShape:
    source = path.read_text(encoding="utf-8")
    prose = mask_non_prose(source)
    return DraftShape(
        path=path,
        han=han_count(prose),
        paragraphs=paragraph_lengths(prose),
        h2=len(re.findall(r"^##\s+\S", prose, re.MULTILINE)),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="比较三篇以上稿件是否套用相同段落骨架")
    parser.add_argument("paths", nargs="+", type=Path, help="至少三份 UTF-8 Markdown 或文本稿")
    parser.add_argument("--strict", action="store_true", help="发现批量同构信号时返回失败")
    args = parser.parse_args()

    if len(args.paths) < 3:
        parser.error("至少提供三份稿件")

    for path in args.paths:
        if not path.exists() or not path.is_file():
            print(f"文件不存在：{path}", file=sys.stderr)
            return 2

    try:
        shapes = [read_shape(path) for path in args.paths]
    except UnicodeDecodeError:
        print("稿件必须是 UTF-8 编码。", file=sys.stderr)
        return 2

    for shape in shapes:
        print(
            f"{shape.path}: 汉字数={shape.han}，正文段={shape.paragraph_count}，"
            f"段长变异系数={shape.paragraph_cv:.2f}，二级标题={shape.h2}"
        )

    signals: list[str] = []
    paragraph_counts = {shape.paragraph_count for shape in shapes}
    if len(paragraph_counts) == 1 and next(iter(paragraph_counts)) >= 8:
        count = next(iter(paragraph_counts))
        signals.append(
            f"[段落数同构] {len(shapes)} 篇稿件都正好有 {count} 个正文段。"
            "回到每篇材料比较触发点、转折位置和自然结束处；不要为了通过检查器随手拆段。"
        )

    if all(shape.paragraph_count >= 8 and shape.paragraph_cv < 0.16 for shape in shapes):
        signals.append(
            "[批量段长过齐] 所有稿件的段长变异系数都低于 0.16。"
            "检查是否把复杂处和简单处修成同样大小的说明单元。"
        )

    if signals:
        print("\n需要人工复核")
        for signal in signals:
            print(f"- {signal}")
    else:
        print("\n未发现这份批量检查器覆盖的同构信号。仍需人工比较推进骨架。")

    return 1 if args.strict and signals else 0


if __name__ == "__main__":
    raise SystemExit(main())
