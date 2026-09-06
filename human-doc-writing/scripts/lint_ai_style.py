#!/usr/bin/env python3
"""为中文成稿提供需要结合文风判断的编辑提醒。

风格与提示分不阻断交付；严格模式只检查内部过程残留和显式最低篇幅。
脚本不判断事实是否可靠，也不替代人工编辑。
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


PROFILES = ("universal", "social-longform", "wechat-longform")
SOCIAL_PROFILES = ("social-longform", "wechat-longform")


@dataclass(frozen=True)
class Rule:
    label: str
    pattern: re.Pattern[str]
    weight: int
    threshold: int
    advice: str


@dataclass(frozen=True)
class Paragraph:
    position: int
    text: str
    han: int
    sentences: int


PROCESS_MARKERS = re.compile(r"<!--\s*source\s*:|\[DISCARDED-[^\]\n]+\]", re.IGNORECASE)


COMMON_RULES = (
    Rule(
        "文档自我定位",
        re.compile(r"文档定位|这是一份[^。\n]{0,40}(?:文档|说明|白皮书)"),
        3,
        1,
        "判断定位说明是否帮助读者；无助于理解时可直接进入问题或事实。",
    ),
    Rule(
        "模板化开头",
        re.compile(r"一句话说明|一文读懂|首先[，,]|本文将|下面(?:将|会)|在当今[^。\n]{0,30}时代|随着[^。\n]{0,30}(?:发展|进步)"),
        2,
        1,
        "背景或预告有实际导航作用时保留；只是套话时可直接写事情、问题或结果。",
    ),
    Rule(
        "解释型路标",
        re.compile(r"简单来说|换句话说|可以(?:把|将).{0,25}理解为|需要明确的是|值得注意的是|这意味着"),
        1,
        2,
        "检查前句是否已经清楚，通常可删除或直接写事实。",
    ),
    Rule(
        "抽象强调词",
        re.compile(r"核心(?:是|能力|理念|回答|重点)|真正(?:完成|重要|被|的)|重点(?:是|不在)|本质上|更深层次|归根结底"),
        1,
        5,
        "用具体事实、动作、成本和后果替代反复强调。",
    ),
    Rule(
        "模板化收束",
        re.compile(r"总的来说|综上所述|最后需要说明|未来可期|让我们共同|让我们一起"),
        2,
        1,
        "判断收束是否增加信息或情绪；只重复前文时可删减。",
    ),
)


TRIPLE_PATTERN = re.compile(r"[\u4e00-\u9fff]{1,6}、[\u4e00-\u9fff]{1,6}、[\u4e00-\u9fff]{1,6}")


STOCK_PHRASES = (
    "说白了",
    "说穿了",
    "先说结论",
)


JARGON_TERMS = (
    "赋能",
    "抓手",
    "商业闭环",
    "价值闭环",
    "能力沉淀",
    "拉通",
    "底层逻辑",
    "顶层设计",
    "认知跃迁",
    "价值释放",
    "能力建设",
    "降本增效",
    "内容矩阵",
    "全链路",
    "组合拳",
    "打开想象空间",
    "结构性机会",
    "关键命题",
    "深层逻辑",
    "技术底座",
    "公共底座",
    "技术主权",
    "单点风险",
    "主脊柱",
    "材料锚点",
    "认知增量",
    "迭代闭环",
)


CONTEXT_JARGON = (
    "沉淀",
    "颗粒度",
    "对齐",
    "协同",
    "链路",
    "生态位",
    "心智",
    "范式",
    "方法论",
    "核心变量",
    "打法",
    "想象空间",
    "闭环",
    "不丢",
)


LYRIC_WORDS = (
    "安放",
    "抵达",
    "微光",
    "褶皱",
    "丰盈",
    "滚烫",
    "轻盈",
    "赤裸",
    "剥开",
    "锋利",
    "坚硬",
    "柔软",
)


ROAD_SIGNS = (
    "更微妙的是",
    "还有一层",
    "只说对了一半",
    "值得注意的是",
    "需要指出的是",
    "从某种意义上说",
)


SOFT_MARKERS = (
    "真正",
    "本质上",
    "更深层次",
    "归根结底",
    "换句话说",
    "不可否认",
    "核心是",
    "关键在于",
    "这意味着",
)


REPEATED_OPENERS = (
    "其实",
    "不过",
    "当然",
    "所以",
    "但是",
    "后来",
    "当时",
    "很多人",
    "问题是",
    "更重要的是",
    "说到这里",
    "它会",
    "用户可以",
    "目标是",
    "当前",
)


PUNCTUATION_SIGNALS = {
    "：": "中文冒号",
    ":": "英文冒号",
    "—": "破折号",
    "–": "连接号式破折号",
}


PIVOT_PATTERNS = (
    re.compile(r"(?:并)?不是[^。！？\n]{0,90}而是"),
    re.compile(r"并非[^。！？\n]{0,90}而是"),
    re.compile(r"不在于[^。！？\n]{0,90}而在于"),
    re.compile(r"与其说[^。！？\n]{0,90}(?:不如|毋宁|倒不如)"),
    re.compile(r"[。！？!?]\s*而是"),
    re.compile(r"表面(?:上)?[^。！？\n]{0,90}(?:其实|实际|实则)"),
    re.compile(r"看似[^。！？\n]{0,90}(?:其实|实际|实则)"),
)


SEMANTIC_PIVOT_PATTERNS = (
    re.compile(r"(?:总|一直|曾|都)?以为[^！？\n]{2,60}?(?:其实|才发现|才明白|才知道|后来才)"),
    re.compile(r"(?:总|都|一直)以为[^！？\n]{2,60}?[。，](?:可|但|其实)"),
    re.compile(r"回头(?:看|一看)?才(?:发现|明白|知道)"),
    re.compile(r"(?:并)?不是[^。！？\n]{1,40}，(?:更|才)?是[^，。！？\n]"),
    re.compile(r"从来(?:都)?(?:不是|与[^。！？，\n]{1,12}无关)"),
    re.compile(r"答案(?:是否定的|恰恰相反)|恰恰相反"),
    re.compile(r"表面(?:上)?[^！？\n]{0,60}。[^！？\n]{0,12}(?:其实|实际|实则)"),
    re.compile(r"看似[^！？\n]{0,60}。[^！？\n]{0,12}(?:其实|实际|实则)"),
    re.compile(r"[^，。！？\n]{1,12}不重要，(?:重要|要紧)的是"),
    re.compile(r"真正[^，。！？\n]{0,16}的(?:，)?是"),
    re.compile(r"不只(?:是)?[^。！？\n]{0,90}(?:还|也)"),
)


NOMINALIZATION_PATTERNS = (
    re.compile(r"进行(?:了|一次|一场|着)?[^。，！？\n]{0,10}(?:调整|优化|升级|分析|讨论|沟通|梳理|复盘|迭代|探索|尝试|思考|规划|布局)"),
    re.compile(r"实现了?[^。，！？\n]{0,14}的?[^。，！？\n]{0,6}(?:提升|增长|突破|转变|跃升|落地)"),
    re.compile(r"完成了?对[^。，！？\n]{0,16}的"),
    re.compile(r"起到了?[^。，！？\n]{0,12}的?作用"),
    re.compile(r"具有[^。，！？\n]{0,10}(?:意义|价值)"),
)


CONJUNCTIONS = (
    "因为",
    "所以",
    "但是",
    "然而",
    "同时",
    "此外",
    "而且",
    "并且",
    "因此",
    "不仅",
)


SOCIAL_MANUAL_PATTERNS = (
    re.compile(r"(?:这里|目前|当前)(?:能|能够|可以)确认的是"),
    re.compile(r"(?:本文|这篇(?:文章|稿件)|文章(?:只|仅|将|会))[^。！？\n]{0,30}(?:讨论|说明|评价|处理|覆盖)"),
    re.compile(r"(?:这|以上|两项|三项|四项)[^。！？\n]{0,20}(?:共同)?构成[^。！？\n]{0,20}(?:范围|框架|体系)"),
    re.compile(r"(?:两套|两个|三种|四项|这些)[^。！？\n]{0,18}(?:承担|负责)[^。！？\n]{0,18}(?:不同|各自)"),
)


WECHAT_PUNCHLINE_PATTERNS = (
    re.compile(
        r"(?:麻烦|问题|关键|难处)(?:恰好|恰恰|正好|偏偏)?(?:出在|在于)"
        r"(?:这种|这个|这里|这份|此处|这一点)[^。！？\n]{0,24}[。！？]"
    ),
    re.compile(r"[^。！？\n]{0,24}(?:在这一刻)?(?:成了|变成了)(?:表象|假象|症状)[。！？]"),
    re.compile(
        r"(?:最先|首先|第一件事)[^。！？\n]{0,24}"
        r"(?:钉住|抓住|按住|撕开|刺穿)[^。！？\n]{0,24}[。！？]"
    ),
)


LEFT_BRANCH_PATTERNS = (
    re.compile(r"(?:^|[。！？]\s*)在[^，。！？\n]{12,70}(?:以后|之后|之前|以前|过程中|情况下|背景下)，"),
    re.compile(r"(?:^|[。！？]\s*)那些[^，。！？\n]{10,60}的[^，。！？\n]{2,30}[，。]"),
    re.compile(r"(?:^|[。！？]\s*)(?:真正|最终|最后)让[^，。！？\n]{8,70}的，是"),
)


METAPHOR_FIELDS = {
    "温度": ("降温", "升温", "冷却", "余温", "温度最高"),
    "生死战争": ("杀死", "死因", "枪响", "开火", "战场", "引爆", "弹药"),
    "建筑灾害": ("坍塌", "崩塌", "地基", "砖头", "支柱", "废墟"),
    "仓储租赁": ("仓库", "库房", "租金", "取货", "入库", "库存"),
    "道路竞赛": ("赛道", "跑道", "岔路", "十字路口", "终点线", "门票"),
    "机器器官": ("齿轮", "引擎", "发动机", "血管", "骨架", "肌肉"),
    "海洋航行": ("蓝海", "浪潮", "潮水", "航船", "灯塔", "彼岸"),
}


META_HEADINGS = re.compile(
    r"^#{2,4}\s*(?:\d+[.、]\s*)?(一句话说明|文档定位|核心理念|适合谁使用|不要误解成什么|未来方向|总结)\s*$",
    re.MULTILINE,
)


def han_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def excerpt(value: str, width: int = 72) -> str:
    clean = re.sub(r"\s+", " ", value).strip()
    return clean if len(clean) <= width else clean[: width - 1] + "…"


def masked_text(text: str) -> str:
    return "".join("\n" if char == "\n" else " " for char in text)


def mask_code(text: str) -> str:
    """先屏蔽 Markdown 代码示例，保留正文和注释供内部残留检查。"""
    lines: list[str] = []
    fence: Optional[str] = None
    in_comment = False
    for line in text.splitlines(keepends=True):
        if fence is not None:
            lines.append(masked_text(line))
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*\r?\n?", line):
                fence = None
            continue
        if in_comment:
            lines.append(line)
            in_comment = "-->" not in line
            continue
        opening = re.match(r" {0,3}(`{3,}|~{3,})", line)
        if opening:
            fence = opening.group(1)
            lines.append(masked_text(line))
        elif line.startswith(("    ", "\t")):
            lines.append(masked_text(line))
        else:
            lines.append(line)
            comment_start = line.find("<!--")
            in_comment = comment_start >= 0 and "-->" not in line[comment_start:]
    fenced = "".join(lines)
    return re.sub(
        r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)",
        lambda match: masked_text(match.group()),
        fenced,
        flags=re.DOTALL,
    )


def mask_non_prose(text: str) -> str:
    """屏蔽代码、网址和机器元数据，同时保留字符位置与换行。"""
    patterns = (
        re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", re.DOTALL),
        re.compile(r"<!--.*?(?:-->|\Z)", re.DOTALL),
        re.compile(r"^[ ]{0,3}\[[^\]\n]+\]:[^\n]*", re.MULTILINE),
        re.compile(r"\]\([^\n)]*\)"),
        re.compile(r"https?://[^\s)>]+"),
        re.compile(r"<[^>\n]+>"),
    )
    masked = mask_code(text)
    for pattern in patterns:
        masked = pattern.sub(lambda match: masked_text(match.group()), masked)
    return masked


def non_overlapping_terms(text: str, terms: tuple[str, ...]) -> list[tuple[int, str]]:
    matches: list[tuple[int, str]] = []
    occupied: list[tuple[int, int]] = []
    for term in sorted(terms, key=len, reverse=True):
        for match in re.finditer(re.escape(term), text):
            start, end = match.span()
            if any(start < old_end and end > old_start for old_start, old_end in occupied):
                continue
            matches.append((start, term))
            occupied.append((start, end))
    return sorted(matches)


def all_matches(text: str, patterns: tuple[re.Pattern[str], ...]) -> list[re.Match[str]]:
    matches: list[re.Match[str]] = []
    for pattern in patterns:
        matches.extend(pattern.finditer(text))
    return sorted(matches, key=lambda match: match.start())


def prose_paragraphs(text: str) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    cursor = 0
    for block in re.split(r"\n\s*\n", text):
        position = text.find(block, cursor)
        cursor = max(position + len(block), cursor)
        clean = re.sub(r"[>*_`]", "", block).strip()
        if not clean or clean.startswith(("#", "http", "![", "```")):
            continue
        if re.match(r"^(?:[-+*]|\d+[.、])\s", clean):
            continue
        count = han_count(clean)
        if count < 4:
            continue
        sentences = max(1, len(re.findall(r"[。！？!?]", clean)))
        paragraphs.append(Paragraph(position, clean, count, sentences))
    return paragraphs


def max_bullet_run(lines: list[str]) -> int:
    longest = current = 0
    for line in lines:
        if re.match(r"^\s*(?:[-*+] |\d+[.)、]\s)", line):
            current += 1
            longest = max(longest, current)
        elif line.strip():
            current = 0
    return longest


def heavy_de_sentences(text: str) -> list[re.Match[str]]:
    matches: list[re.Match[str]] = []
    for match in re.finditer(r"[^。！？!?\n]+(?:[。！？!?]|$)", text):
        value = match.group()
        if han_count(value) >= 38 and value.count("的") >= 4:
            matches.append(match)
    return matches


def anaphora_runs(text: str, minimum: int = 3) -> list[re.Match[str]]:
    """找出同一句里三个以上小句使用同一开头的排比。"""

    matches: list[re.Match[str]] = []
    for sentence in re.finditer(r"[^。！？!?\n]+(?:[。！？!?]|$)", text):
        clauses = [
            clause.strip()
            for clause in re.split(r"[，、；,;]", sentence.group())
            if han_count(clause) >= 3
        ]
        if len(clauses) < minimum:
            continue
        run = 1
        for previous, current in zip(clauses, clauses[1:]):
            if previous[:2] == current[:2] and re.match(r"[\u4e00-\u9fff]{2}", current):
                run += 1
                if run >= minimum:
                    matches.append(sentence)
                    break
            else:
                run = 1
    return matches


def coefficient_of_variation(values: list[int]) -> Optional[float]:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    if mean == 0:
        return None
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return (variance**0.5) / mean


def sentence_length_cv(text: str) -> Optional[tuple[float, int]]:
    """返回句长变异系数和可识别句子数。"""

    lengths = [
        han_count(match.group())
        for match in re.finditer(r"[^。！？!?\n]+[。！？!?]", text)
        if han_count(match.group()) >= 4
    ]
    if len(lengths) < 12:
        return None
    value = coefficient_of_variation(lengths)
    return (value, len(lengths)) if value is not None else None


def bracket_highlights(text: str) -> list[re.Match[str]]:
    return list(re.finditer(r"[「『][^」』\n]{1,6}[」』]", text))


def short_streak(paragraphs: list[Paragraph], limit: int = 4) -> Optional[list[Paragraph]]:
    streak: list[Paragraph] = []
    for paragraph in paragraphs:
        if paragraph.han <= 24 and paragraph.sentences <= 1:
            streak.append(paragraph)
            if len(streak) >= limit:
                return streak
        else:
            streak = []
    return None


def metaphor_cluster(
    text: str, distance: int = 800
) -> Optional[tuple[list[tuple[int, str, str]], set[str]]]:
    hits: list[tuple[int, str, str]] = []
    for field, words in METAPHOR_FIELDS.items():
        for word in words:
            for match in re.finditer(re.escape(word), text):
                hits.append((match.start(), field, word))
    hits.sort()
    for index, (start, _, _) in enumerate(hits):
        window = [hit for hit in hits[index:] if hit[0] - start <= distance]
        fields = {hit[1] for hit in window}
        if len(fields) >= 3:
            return window, fields
    return None


def add_pattern_signals(
    source: str,
    prose: str,
    warnings: list[str],
) -> int:
    score = 0
    for rule in COMMON_RULES:
        matches = list(rule.pattern.finditer(prose))
        if len(matches) < rule.threshold:
            continue
        weighted = rule.weight * max(1, len(matches) - rule.threshold + 1)
        score += weighted
        lines = "、".join(str(line_number(source, match.start())) for match in matches[:8])
        message = f"[{rule.label}] {len(matches)} 处，第 {lines} 行。{rule.advice}"
        warnings.append(message)
    return score


def check(
    path: Path, profile: str, min_han: Optional[int] = None
) -> tuple[int, int, list[str], list[str]]:
    source = path.read_text(encoding="utf-8")
    prose = mask_non_prose(source)
    failures = [
        f"[过程标注残留] 第 {line_number(source, match.start())} 行。删除内部来源注释或弃稿标记。"
        for match in PROCESS_MARKERS.finditer(mask_code(source))
    ]
    warnings: list[str] = []
    score = add_pattern_signals(source, prose, warnings)

    total_han = han_count(prose)
    if min_han is not None and total_han < min_han:
        failures.append(
            f"[篇幅不足] 当前 {total_han} 个汉字，文档契约最低 {min_han}。"
            "按本篇需要补足解释、过程、条件或感受；材料不足时明确缩小篇幅，不靠空话补字数。"
        )

    triple_matches = list(TRIPLE_PATTERN.finditer(prose))
    if len(triple_matches) >= 5:
        score += min(3, len(triple_matches) - 4) if profile in SOCIAL_PROFILES else 1
        lines = "、".join(str(line_number(source, match.start())) for match in triple_matches[:8])
        warnings.append(
            f"[口号式三连] {len(triple_matches)} 处，第 {lines} 行。"
            "分类、字段和有效排比可以保留；结合语境判断是否增加理解、节奏或情绪。"
        )

    meta = META_HEADINGS.findall(prose)
    if meta:
        score += 2 * len(meta)
        warnings.append(f"[模板章节] {len(meta)} 个，{'、'.join(meta)}。确认是否真的服务读者。")

    h2_count = len(re.findall(r"^##\s+\S", prose, re.MULTILINE))
    if profile in SOCIAL_PROFILES and total_han <= 2200 and h2_count >= 2:
        score += 1
        warnings.append(
            f"[短稿小标题] {total_han} 个汉字使用 {h2_count} 个二级标题。"
            "标题有助于导航或阅读节奏时保留；妨碍连续阅读时再考虑合并或删减。"
        )

    if profile in SOCIAL_PROFILES:
        manual_matches = all_matches(prose, SOCIAL_MANUAL_PATTERNS)
        if manual_matches:
            score += min(3, len(manual_matches))
            samples = "；".join(
                f"第 {line_number(source, match.start())} 行“{excerpt(match.group(), 44)}”"
                for match in manual_matches[:4]
            )
            warnings.append(
                f"[说明书口吻] 共 {len(manual_matches)} 处。{samples}。"
                "核验留在后台，正文优先写动作、选择和后果；职责分类确有必要时再保留。"
            )

    visible = [line for line in prose.splitlines() if line.strip()]
    bullet_lines = sum(bool(re.match(r"^\s*(?:[-*+] |\d+[.)、]\s)", line)) for line in visible)
    if visible and bullet_lines / len(visible) > 0.35:
        score += 2
        warnings.append(f"[列表密度] {bullet_lines}/{len(visible)} 个非空行是列表。检查是否在机械盘点。")

    run = max_bullet_run(visible)
    if run >= 9:
        score += 1
        warnings.append(f"[长列表] 最长连续列表 {run} 项。考虑分组、删减或增加解释层次。")

    paragraphs = prose_paragraphs(prose)
    if len(paragraphs) >= 10:
        one_sentence = sum(paragraph.sentences <= 1 for paragraph in paragraphs)
        ratio = one_sentence / len(paragraphs)
        if ratio >= 0.75:
            score += 1
            warnings.append(f"[段落鼓点] {ratio:.0%} 的段落只有一句话。检查是否统一切成海报文案。")

    if profile in SOCIAL_PROFILES and len(paragraphs) >= 8:
        paragraph_cv = coefficient_of_variation([paragraph.han for paragraph in paragraphs])
        if paragraph_cv is not None and paragraph_cv < 0.16:
            score += 1
            warnings.append(
                f"[段落过齐] {len(paragraphs)} 个正文段的长度变异系数为 {paragraph_cv:.2f}。"
                "检查是否把每段修成相近长度和单一功能；不要为通过检查器机械拆段。"
            )

    streak = short_streak(paragraphs)
    if streak:
        score += 1
        warnings.append(
            f"[短句排队] 从第 {line_number(source, streak[0].position)} 行起连续出现 {len(streak)} 个短促单句段。"
        )

    opener_counts: collections.Counter[str] = collections.Counter()
    opener_positions: dict[str, int] = {}
    for paragraph in paragraphs:
        value = paragraph.text.lstrip("“‘\"（(")
        for opener in REPEATED_OPENERS:
            if value.startswith(opener):
                opener_counts[opener] += 1
                opener_positions.setdefault(opener, paragraph.position)
                break
    repeated = [(opener, count) for opener, count in opener_counts.items() if count >= 4]
    if repeated:
        score += sum(count - 3 for _, count in repeated)
        details = "、".join(f"{opener} {count} 次" for opener, count in repeated)
        first = min(opener_positions[opener] for opener, _ in repeated)
        warnings.append(f"[重复句首] 第 {line_number(source, first)} 行附近开始，{details}。")

    left_branches = all_matches(prose, LEFT_BRANCH_PATTERNS)
    left_limit = max(2, han_count(prose) // 1200)
    if len(left_branches) > left_limit:
        score += 1
        samples = "；".join(
            f"第 {line_number(source, match.start())} 行“{excerpt(match.group(), 44)}”"
            for match in left_branches[:4]
        )
        warnings.append(f"[长前置成分] 共 {len(left_branches)} 处，主干可能来得太晚。{samples}")

    dense_de = heavy_de_sentences(prose)
    dense_limit = max(1, han_count(prose) // 1500)
    if len(dense_de) > dense_limit:
        score += 1
        samples = "；".join(
            f"第 {line_number(source, match.start())} 行“{excerpt(match.group(), 44)}”"
            for match in dense_de[:4]
        )
        warnings.append(f"[重定语句] {len(dense_de)} 句含四个以上的“的”。{samples}")

    marker_matches = non_overlapping_terms(prose, SOFT_MARKERS)
    marker_limit = max(2, han_count(prose) // 900)
    if len(marker_matches) > marker_limit:
        score += 1
        samples = "、".join(dict.fromkeys(term for _, term in marker_matches))
        warnings.append(f"[洞察路标] 共 {len(marker_matches)} 处，提醒线 {marker_limit} 处。重点检查 {samples}。")

    if profile in SOCIAL_PROFILES:
        anaphoras = anaphora_runs(prose)
        if anaphoras:
            score += 1
            samples = "；".join(
                f"第 {line_number(source, match.start())} 行“{excerpt(match.group(), 44)}”"
                for match in anaphoras[:4]
            )
            warnings.append(
                f"[同构排比] 共 {len(anaphoras)} 处。{samples}。"
                "判断重复是否推进信息、节奏或情绪；有作用时可以保留。"
            )

        nominalizations = all_matches(prose, NOMINALIZATION_PATTERNS)
        if nominalizations:
            score += 1
            samples = "；".join(
                f"第 {line_number(source, match.start())} 行“{excerpt(match.group(), 36)}”"
                for match in nominalizations[:4]
            )
            warnings.append(
                f"[名词化] 共 {len(nominalizations)} 处。{samples}。还原成谁做了什么和结果怎样变化。"
            )

        conjunction_hits = non_overlapping_terms(prose, CONJUNCTIONS)
        if total_han >= 600 and len(conjunction_hits) * 1000 / total_han > 7:
            score += 1
            counts = collections.Counter(term for _, term in conjunction_hits)
            samples = "、".join(f"{term} {count} 次" for term, count in counts.most_common(4))
            warnings.append(
                f"[连词过密] 每千字约 {len(conjunction_hits) * 1000 // total_han} 个。{samples}。"
                "连词有助于读者跟上关系时保留；只重复语序已表达的关系时可删减。"
            )

        lyric_matches = non_overlapping_terms(prose, LYRIC_WORDS)
        if len(lyric_matches) >= 2:
            score += 1
            samples = "、".join(dict.fromkeys(term for _, term in lyric_matches))
            warnings.append(
                f"[抒情词] 共 {len(lyric_matches)} 处，出现 {samples}。"
                "结合所选文风判断意象是否帮助感知或传情；成立时保留。"
            )

        highlights = bracket_highlights(prose)
        highlight_limit = max(3, total_han // 700)
        if len(highlights) > highlight_limit:
            score += 1
            samples = "、".join(dict.fromkeys(match.group() for match in highlights[:6]))
            warnings.append(
                f"[高亮短语] 「」短语共 {len(highlights)} 处，例词有 {samples}。检查是否在批量造金句。"
            )

        sentence_cv = sentence_length_cv(prose)
        if sentence_cv and sentence_cv[0] < 0.42:
            score += 1
            warnings.append(
                f"[句长过齐] {sentence_cv[1]} 个句子的长度变异系数为 {sentence_cv[0]:.2f}。"
                "复杂处放开写，简单处压短；不要为通过检查器硬塞短句。"
            )

    context_matches = non_overlapping_terms(prose, CONTEXT_JARGON)
    jargon_spans = [(position, position + len(term)) for position, term in non_overlapping_terms(prose, JARGON_TERMS)]
    context_matches = [
        (position, term)
        for position, term in context_matches
        if not any(position < end and position + len(term) > start for start, end in jargon_spans)
    ]
    if context_matches:
        samples = "、".join(dict.fromkeys(term for _, term in context_matches))
        lines = "、".join(
            dict.fromkeys(str(line_number(source, position)) for position, _ in context_matches[:8])
        )
        warnings.append(f"[语境词] 第 {lines} 行出现 {samples}。本义准确时保留，用来抬价时改写。")

    metaphors = metaphor_cluster(prose)
    if metaphors:
        score += 1
        window, fields = metaphors
        samples = "、".join(dict.fromkeys(hit[2] for hit in window))
        warnings.append(
            f"[意象语境] 八百字内出现 {len(fields)} 组词，例词有 {samples}。"
            "可能是本义或借喻；只在意象跳换妨碍理解时调整。"
        )

    if profile in SOCIAL_PROFILES:
        for symbol, label in PUNCTUATION_SIGNALS.items():
            matches = list(re.finditer(re.escape(symbol), prose))
            if symbol in ("：", ":"):
                context_matches: list[re.Match[str]] = []
                for match in matches:
                    if (
                        match.start() > 0
                        and match.end() < len(prose)
                        and prose[match.start() - 1].isdigit()
                        and prose[match.end()].isdigit()
                    ):
                        continue
                    tail = prose[match.end() :].lstrip()
                    if tail[:1] in ("「", "『", "“", "‘", '"'):
                        continue
                    context_matches.append(match)
                matches = context_matches
            if matches:
                lines = "、".join(str(line_number(source, match.start())) for match in matches[:8])
                warnings.append(
                    f"[{label}] 共 {len(matches)} 处，第 {lines} 行。"
                    "用于清楚表达关系或安排停顿时保留；不需要为消除提示改写引语。"
                )

        for position, phrase in non_overlapping_terms(prose, STOCK_PHRASES):
            warnings.append(
                f"[口语路标] 第 {line_number(source, position)} 行，{phrase}。"
                "符合说话人的语气或帮助读者理解时保留。"
            )

        for position, phrase in non_overlapping_terms(prose, JARGON_TERMS):
            warnings.append(
                f"[词语语境] 第 {line_number(source, position)} 行，{phrase}。"
                "本义、引语或精确术语可以保留；只用来抬价时再改写。"
            )

        for phrase in ROAD_SIGNS:
            for match in re.finditer(re.escape(phrase), prose):
                warnings.append(
                    f"[解释路标] 第 {line_number(source, match.start())} 行，{phrase}。"
                    "判断是否确实提示了新的信息关系，有作用时保留。"
                )

        pivot_matches = all_matches(prose, PIVOT_PATTERNS)
        for match in pivot_matches:
            warnings.append(
                f"[对比与修正] 第 {line_number(source, match.start())} 行，“{excerpt(match.group())}”。"
                "真实纠错、有效对比和引语可以保留；只在制造假误解时调整。"
            )

        occupied = [match.span() for match in pivot_matches]
        semantic_pivots: list[re.Match[str]] = []
        for match in all_matches(prose, SEMANTIC_PIVOT_PATTERNS):
            if any(match.start() < end and match.end() > start for start, end in occupied):
                continue
            semantic_pivots.append(match)
            occupied.append(match.span())
        if semantic_pivots:
            score += 1
            samples = "；".join(
                f"第 {line_number(source, match.start())} 行“{excerpt(match.group(), 44)}”"
                for match in semantic_pivots[:4]
            )
            warnings.append(
                f"[疑似翻案腔] 共 {len(semantic_pivots)} 处。{samples}。"
                "确实走过误解与修正时保留，先立假误解再抬价时改成正面判断。"
            )

    if profile == "wechat-longform":
        questions = list(re.finditer(r"[？?]", prose))
        if questions:
            lines = "、".join(str(line_number(source, match.start())) for match in questions[:8])
            warnings.append(
                f"[提问语境] 共 {len(questions)} 处，第 {lines} 行。"
                "真实提问、必要设问与人物原话可以保留；只检查是否在反复制造空悬念。"
            )

        for match in all_matches(prose, WECHAT_PUNCHLINE_PATTERNS):
            warnings.append(
                f"[点题语境] 第 {line_number(source, match.start())} 行，“{excerpt(match.group())}”。"
                "确有事实、解释或情绪作用时保留。"
            )

    return total_han, score, failures, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="提供中文成稿的编辑提醒；风格信号与提示分不决定通过或失败")
    parser.add_argument("path", type=Path, help="UTF-8 Markdown 或纯文本文件")
    parser.add_argument("--profile", choices=PROFILES, default="universal", help="兼容的提醒范围，不设置文风禁令")
    parser.add_argument(
        "--min-han",
        type=int,
        help="文档契约允许的最低汉字数；只在材料已经足够时使用",
    )
    parser.add_argument("--strict", action="store_true", help="仅内部过程残留或显式最低篇幅未满足时返回 1；风格提醒不阻断")
    args = parser.parse_args()

    if args.min_han is not None and args.min_han <= 0:
        parser.error("--min-han 必须是正整数")

    if not args.path.exists() or not args.path.is_file():
        print(f"文件不存在：{args.path}", file=sys.stderr)
        return 2

    try:
        total_han, score, failures, warnings = check(args.path, args.profile, args.min_han)
    except UnicodeDecodeError:
        print("文件必须是 UTF-8 编码。", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"无法读取文件：{exc}", file=sys.stderr)
        return 2

    print(f"{args.path}: profile={args.profile}，汉字数={total_han}，提示分={score}，阻断项={len(failures)}")

    if failures:
        print("\n必须修改")
        for item in failures:
            print(f"- {item}")

    if warnings:
        print("\n编辑提醒（结合语境和所选文风判断，可以保留；提示分不影响退出状态）")
        for item in warnings:
            print(f"- {item}")

    if not failures and not warnings:
        print("\n未发现这份检查器覆盖的问题。仍需人工核对事实、材料、推进和人味。")

    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
