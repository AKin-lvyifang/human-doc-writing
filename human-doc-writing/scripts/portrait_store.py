#!/usr/bin/env python3
"""Store and manage human-doc-writing portraits.

The script intentionally stores plain Markdown. It backs up an active portrait
before replacement and rebuilds a small human-readable index.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

TYPE_NAMES = {
    "explainer": "说明文",
    "product-doc": "产品文档",
    "how-to": "教程/帮助文档",
    "prd": "PRD",
    "github-readme": "GitHub README",
    "github-release": "GitHub Release/CHANGELOG",
    "wechat-article": "公众号文章",
    "xiaohongshu": "小红书内容",
    "social-article": "社媒中长文",
    "commentary": "观点评论",
    "narrative": "纪实/人物/经历",
    "essay": "随笔/散文/读书",
}

KIND_DIRS = {
    "positive": "portraits",
    "negative": "anti-patterns",
}


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def user_root() -> Path:
    return skill_root() / "user"


def validate_name(name: str | None) -> None:
    if name is not None and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("画像名称只能使用小写英文字母、数字和连接各段的连字符。")


def check_storage_path(path: Path) -> Path:
    if not path.resolve().is_relative_to(user_root().resolve()):
        raise ValueError("画像路径不能越出 user 目录。")
    return path


def active_path(type_id: str, kind: str, name: str | None = None) -> Path:
    validate_type(type_id)
    validate_name(name)
    folder = user_root() / KIND_DIRS[kind]
    target = folder / type_id / f"{name}.md" if name else folder / f"{type_id}.md"
    return check_storage_path(target)


def history_dir() -> Path:
    return check_storage_path(user_root() / "history")


def ensure_dirs() -> None:
    for dirname in KIND_DIRS.values():
        check_storage_path(user_root() / dirname).mkdir(parents=True, exist_ok=True)
    history_dir().mkdir(parents=True, exist_ok=True)


def validate_type(type_id: str) -> None:
    if type_id not in TYPE_NAMES:
        allowed = ", ".join(TYPE_NAMES)
        raise ValueError(f"未知类型：{type_id}。允许值：{allowed}")


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def backup(path: Path, kind: str, type_id: str, name: str | None = None) -> Path | None:
    if not path.exists():
        return None
    stem = f"{type_id}-{kind}{'-' + name if name else ''}-{timestamp()}"
    suffix = 0
    while True:
        target = history_dir() / f"{stem}{'-' + str(suffix) if suffix else ''}.md"
        try:
            with target.open("x", encoding="utf-8") as handle:
                handle.write(path.read_text(encoding="utf-8"))
            return target
        except FileExistsError:
            suffix += 1


def first_heading(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return path.stem


def source_line(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("- 来源："):
                return line.removeprefix("- 来源：").strip()
    except OSError:
        pass
    return "未记录"


def iter_active() -> Iterable[tuple[str, str, Path]]:
    for kind, dirname in KIND_DIRS.items():
        folder = user_root() / dirname
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            yield kind, path.stem, check_storage_path(path)
        for type_id in TYPE_NAMES:
            for path in sorted((folder / type_id).glob("*.md")):
                validate_name(path.stem)
                yield kind, type_id, check_storage_path(path)


def render_index() -> str:
    rows = []
    for kind, type_id, path in iter_active():
        display = TYPE_NAMES.get(type_id, type_id)
        kind_name = "正向" if kind == "positive" else "反例"
        modified = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        name = "默认" if path.parent.name == KIND_DIRS[kind] else path.stem
        rows.append((display, kind_name, name, first_heading(path), source_line(path), modified, path))

    lines = ["# 当前写作画像", ""]
    if not rows:
        lines.extend([
            "暂时没有用户画像。",
            "",
            "把完整文章或链接交给 Codex，并说明要学习或记住其中的写法，即可建立画像。",
        ])
    else:
        lines.extend([
            "| 类型 | 画像 | 变体 | 名称 | 来源 | 更新时间 | 相对路径 |",
            "|---|---|---|---|---|---|---|",
        ])
        for display, kind_name, name, title, source, modified, path in rows:
            safe_source = source.replace("|", "\\|")
            safe_title = title.replace("|", "\\|")
            relative = path.relative_to(user_root()).as_posix()
            lines.append(f"| {display} | {kind_name} | {name} | {safe_title} | {safe_source} | {modified} | `{relative}` |")
    lines.append("")
    return "\n".join(lines)


def rebuild_index() -> Path:
    index = check_storage_path(user_root() / "portrait-index.md")
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(render_index(), encoding="utf-8")
    return index


def cmd_save(args: argparse.Namespace) -> int:
    name = getattr(args, "name", None)
    target = active_path(args.type, args.kind, name)
    profile = Path(args.profile).expanduser().resolve()
    if not profile.is_file():
        raise FileNotFoundError(f"画像文件不存在：{profile}")
    content = profile.read_text(encoding="utf-8")
    if content.lstrip().startswith("---"):
        raise ValueError("画像不应使用 YAML frontmatter。")
    if not content.lstrip().startswith("# "):
        raise ValueError("画像必须是普通 Markdown，并以一级标题开头。")

    if profile == target.resolve():
        raise ValueError("输入画像已经位于保存目标，请使用另一份待保存文件。")
    ensure_dirs()
    target.parent.mkdir(parents=True, exist_ok=True)
    old_backup = backup(target, args.kind, args.type, name)
    shutil.copy2(profile, target)
    index = rebuild_index()

    print(f"已保存：{target}")
    if old_backup:
        print(f"旧画像备份：{old_backup}")
    else:
        print("旧画像：无")
    print(f"索引：{index}")
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    print(render_index())
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    validate_type(args.type)
    path = active_path(args.type, args.kind, getattr(args, "name", None))
    if not path.exists():
        print("没有找到对应画像。")
        return 1
    print(path.read_text(encoding="utf-8"))
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    validate_type(args.type)
    name = getattr(args, "name", None)
    path = active_path(args.type, args.kind, name)
    if not path.exists():
        print("没有对应画像，无需重置。")
        return 0
    ensure_dirs()
    old_backup = backup(path, args.kind, args.type, name)
    path.unlink()
    rebuild_index()
    print(f"已移除：{path}")
    if old_backup:
        print(f"旧画像备份：{old_backup}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="管理 human-doc-writing 写作画像")
    sub = parser.add_subparsers(dest="command", required=True)

    save = sub.add_parser("save", help="保存画像；同名更新前备份，不影响其他写法")
    save.add_argument("--type", required=True, choices=sorted(TYPE_NAMES))
    save.add_argument("--kind", choices=sorted(KIND_DIRS), default="positive")
    save.add_argument("--name", help="可选写法名称，如 warm-observation；省略时保存类型默认画像")
    save.add_argument("--profile", required=True, help="待保存的 Markdown 画像文件")
    save.set_defaults(func=cmd_save)

    list_cmd = sub.add_parser("list", help="只读列出默认与具名画像及路径")
    list_cmd.set_defaults(func=cmd_list)

    show = sub.add_parser("show", help="显示一份当前画像")
    show.add_argument("--type", required=True, choices=sorted(TYPE_NAMES))
    show.add_argument("--kind", choices=sorted(KIND_DIRS), default="positive")
    show.add_argument("--name", help="具名画像；省略时显示类型默认画像")
    show.set_defaults(func=cmd_show)

    reset = sub.add_parser("reset", help="移除当前画像并保留历史备份")
    reset.add_argument("--type", required=True, choices=sorted(TYPE_NAMES))
    reset.add_argument("--kind", choices=sorted(KIND_DIRS), default="positive")
    reset.add_argument("--name", help="只移除这一具名画像；省略时只移除类型默认画像")
    reset.set_defaults(func=cmd_reset)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except (OSError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
