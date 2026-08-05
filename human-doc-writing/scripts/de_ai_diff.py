#!/usr/bin/env python3
"""Compare a draft before and after de-AI/style editing.

The report is an editing signal. It checks whether the rewrite actually changed
surface patterns and whether common AI-style phrases decreased. It does not
judge factual quality or replace human review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path


PHRASES = [
    "本文将",
    "下面将",
    "一句话说明",
    "一文读懂",
    "简单来说",
    "换句话说",
    "需要明确的是",
    "值得注意的是",
    "核心理念",
    "总的来说",
    "综上所述",
    "未来可期",
    "说白了",
    "说穿了",
    "先说结论",
    "更微妙的是",
    "还有一层",
    "只说对了一半",
    "需要指出的是",
    "从某种意义上说",
    "底层逻辑",
    "认知跃迁",
    "价值释放",
]


def read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"文件不存在：{path}")
    return path.read_text(encoding="utf-8")


def paragraphs(text: str) -> list[str]:
    items = [re.sub(r"\s+", " ", item).strip() for item in re.split(r"\n\s*\n", text)]
    return [item for item in items if item]


def phrase_counts(text: str) -> Counter[str]:
    return Counter({phrase: text.count(phrase) for phrase in PHRASES if text.count(phrase)})


def changed_paragraph_ratio(before: list[str], after: list[str]) -> float:
    if not after:
        return 0.0
    before_set = set(before)
    changed = sum(1 for item in after if item not in before_set)
    return changed / len(after)


def build_report(before_path: Path, after_path: Path) -> dict[str, object]:
    before = read_text(before_path)
    after = read_text(after_path)
    before_paras = paragraphs(before)
    after_paras = paragraphs(after)
    before_counts = phrase_counts(before)
    after_counts = phrase_counts(after)
    all_phrases = sorted(set(before_counts) | set(after_counts))

    return {
        "before": str(before_path),
        "after": str(after_path),
        "chars": {"before": len(before), "after": len(after), "delta": len(after) - len(before)},
        "paragraphs": {
            "before": len(before_paras),
            "after": len(after_paras),
            "changed_after_ratio": round(changed_paragraph_ratio(before_paras, after_paras), 3),
        },
        "similarity": round(SequenceMatcher(None, before_paras, after_paras).ratio(), 3),
        "phrase_changes": [
            {
                "phrase": phrase,
                "before": before_counts.get(phrase, 0),
                "after": after_counts.get(phrase, 0),
                "delta": after_counts.get(phrase, 0) - before_counts.get(phrase, 0),
            }
            for phrase in all_phrases
        ],
    }


def print_markdown(report: dict[str, object]) -> None:
    print("# 去 AI 味前后对照报告")
    print()
    print(f"- 原稿：{report['before']}")
    print(f"- 改写稿：{report['after']}")
    chars = report["chars"]
    paras = report["paragraphs"]
    assert isinstance(chars, dict)
    assert isinstance(paras, dict)
    print(f"- 字符数：{chars['before']} -> {chars['after']}（{chars['delta']:+}）")
    print(f"- 段落数：{paras['before']} -> {paras['after']}")
    print(f"- 改写覆盖信号：{paras['changed_after_ratio']}")
    print(f"- 段落相似度：{report['similarity']}")
    print()
    print("## 口吻词变化")
    changes = report["phrase_changes"]
    if not changes:
        print()
        print("未命中内置口吻词。仍需人工检查结构、事实和节奏。")
        return
    print()
    print("| 词 | 原稿 | 改写稿 | 变化 |")
    print("|---|---:|---:|---:|")
    for item in changes:
        print(f"| {item['phrase']} | {item['before']} | {item['after']} | {item['delta']:+} |")


def main() -> int:
    parser = argparse.ArgumentParser(description="生成中文稿件去 AI 味前后对照报告")
    parser.add_argument("--before", required=True, type=Path, help="原稿路径")
    parser.add_argument("--after", required=True, type=Path, help="改写稿路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    try:
        report = build_report(args.before.expanduser().resolve(), args.after.expanduser().resolve())
    except (OSError, UnicodeDecodeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_markdown(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
