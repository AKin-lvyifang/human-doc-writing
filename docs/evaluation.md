# 融合评测 / Integration evaluation

## 中文

### 目的

这次评测不是证明某个 Skill 永远更好，而是检查把 KKKKhazix `human-writing` 的方法融合进个人画像系统后，是否损失了材料真实性、自然推进和普通白话的克制。

### 方法

- 在读稿前固定三个议题和七维评分量表。
- 独立 `human-writing` 与融合版使用相同材料，不查询外部资料。
- 初评时隐藏 A/B 身份，由独立编辑逐篇评分。
- 第一版融合出现系统性问题后，只修复固定小标题、重复解释和内部报告感，再用同一量表评审 C 组。
- 发布后，用户逐段比较前两组独立版与融合版样稿，并用截图标出自设问句、孤立点题短句和动作借喻。
- v1.1 样稿是在相同事实材料上做的定向编辑回归，不是一次新的盲测生成，因此不追加主观分数。
- 所有修订样稿同时运行上游 `check_prose.py` 和融合版 `lint_ai_style.py --profile wechat-longform --strict`。

### 历史评分

| 议题 | 第一版融合 | 独立版 | v1.0 融合版 |
|---|---:|---:|---:|
| GPT-5.6 长任务 | 91 | 93 | **96** |
| 七个 UI Skills | 83 | 86 | **89** |
| 画像与统一门禁 | 91 | **95** | **95** |
| **平均分** | **88.3** | **91.3** | **93.3** |

这组分数曾让我们误以为 v1.0 融合版已经超过独立版。真实阅读反馈表明，量表没有充分惩罚作者自设问句、紧接着自答、孤立的意味深长短句和动作借喻。检查器硬项为零也没有发现这些问题。

### v1.1 纠偏

公众号默认写法重新对齐独立 `human-writing` 的普通白话顺序。先写事实和动作，再写过程、原因、边界与处理办法。读者可能追问什么只用于内部排序，不原样写进正文。

新增 `wechat-longform` 检查档和两份回归夹具。旧融合样稿中的问号、“麻烦恰好出在这种认真里”、“工具数量在这一刻成了表象”和“最先需要钉住”会被阻断；直接陈述相同事实的正向夹具和修订样稿可以通过。

修订后的前两篇融合样稿主动贴近独立版，不再为了显示融合特色增加悬念、发现弧和金句。这里的目标是消除不必要的风格偏移，不是证明融合版必须写出不同句子。

### 边界

- 评测只覆盖三篇中文公众号现实观点稿。
- 分数来自固定量表下的编辑判断，不代表统计学显著性。
- 93.3 是 v1.0 的历史分数，不能再用来证明融合版更自然或更好。
- v1.1 修订样稿是针对已知失败的编辑回归，仍需要后续真实公众号任务和用户阅读继续验收。
- 检查器硬项为零不等于事实已经被外部来源证明。
- README、PRD、教程和小红书有类型卡与检查档，但不应从这组文章分数推断它们同样领先。

样稿见 [examples/evaluation](../examples/evaluation/README.md)。

## English

### Goal

This evaluation does not claim that one skill is universally superior. It checks whether incorporating methods from KKKKhazix `human-writing` into a profile-based writing system preserves material integrity, natural progression, and restrained plain Chinese prose.

### Method

- Three topics and a seven-dimension rubric were fixed before reading any draft.
- Standalone `human-writing` and the integrated skill received the same source material without external research.
- A/B identities were hidden during the first editorial review.
- After recurring issues appeared in the initial integration, only fixed subheadings, repeated explanations, and internal-report tone were addressed. The C group was reviewed with the same rubric.
- After release, the user compared the first two standalone and integrated articles line by line and marked self-authored questions, standalone punchlines, and action metaphors in screenshots.
- Version 1.1 samples are targeted editorial regressions over the same facts, not a new blind generation, so no new subjective score is added.
- Every revised article is checked by upstream `check_prose.py` and integrated `lint_ai_style.py --profile wechat-longform --strict`.

### Historical scores

| Topic | Initial integration | Standalone | v1.0 integration |
|---|---:|---:|---:|
| GPT-5.6 long-running task | 91 | 93 | **96** |
| Seven UI Skills | 83 | 86 | **89** |
| Profiles and universal gate | 91 | **95** | **95** |
| **Mean** | **88.3** | **91.3** | **93.3** |

These scores once suggested that the v1.0 integration had surpassed the standalone version. Reader feedback showed that the rubric underweighted self-authored questions followed by immediate answers, standalone “meaningful” sentences, and unnecessary action metaphors. Zero hard checker failures did not expose them.

### Version 1.1 correction

Default WeChat nonfiction is realigned with the standalone `human-writing` plain-prose order. State facts and actions first, then process, causes, boundaries, and remedies. Anticipated reader questions remain an internal ordering device rather than appearing verbatim in the article.

A new `wechat-longform` profile and two regression fixtures were added. It blocks the question mark and the Chinese patterns equivalent to “the trouble lies precisely in this seriousness,” “the tool count became a mere surface,” and “the first thing to pin down,” while the direct factual fixture and revised samples pass.

The first two revised integration samples intentionally stay close to the standalone version. The goal is to remove unnecessary stylistic drift, not to prove that an integration must produce different sentences.

### Limitations

- The test covers three Chinese nonfiction WeChat-style articles only.
- Scores are editorial judgments under a fixed rubric, not statistical evidence.
- The 93.3 score belongs to v1.0 and is no longer evidence that the integration reads more naturally or is better.
- Version 1.1 samples are targeted regressions for known failures and still require validation in future real WeChat writing tasks.
- Zero hard checker failures do not prove external factual correctness.
- Type cards exist for READMEs, PRDs, tutorials, and Xiaohongshu, but this article test does not establish equal gains for those formats.

See [the paired samples](../examples/evaluation/README.md).
