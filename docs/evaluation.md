# 融合评测 / Integration evaluation

## 中文

### 目的

这次评测不是证明某个 Skill 永远更好，而是检查把 KKKKhazix `human-writing` 的方法融合进个人画像系统后，是否损失了原有的材料真实性和自然推进。

### 方法

- 在读稿前固定三个议题和七维评分量表。
- 独立 `human-writing` 与融合版使用相同材料，不查询外部资料。
- 初评时隐藏 A/B 身份，由独立编辑逐篇评分。
- 第一版融合出现系统性问题后，只修复固定小标题、重复解释和内部报告感，再用同一量表评审 C 组。
- 所有最终样稿同时运行上游 `check_prose.py` 和融合版 `lint_ai_style.py --profile social-longform --strict`。

### 结果

| 议题 | 第一版融合 | 独立版 | 最终融合 |
|---|---:|---:|---:|
| GPT-5.6 长任务 | 91 | 93 | **96** |
| 七个 UI Skills | 83 | 86 | **89** |
| 画像与统一门禁 | 91 | **95** | **95** |
| **平均分** | **88.3** | **91.3** | **93.3** |

最终融合版保住了独立版的连续主线和删减力度，同时恢复了更明确的作者位置。剩余问题主要是某些内部建设题材仍会出现术语偏多，以及 UI Skills 稿尾部仍可更早结束。

### 边界

- 评测只覆盖三篇中文公众号现实观点稿。
- 分数来自固定量表下的编辑判断，不代表统计学显著性。
- 检查器硬项为零不等于事实已经被外部来源证明。
- README、PRD、教程和小红书有类型卡与检查档，但不应从这组文章分数推断它们同样领先。

样稿见 [examples/evaluation](../examples/evaluation/README.md)。

## English

### Goal

This evaluation does not claim that one skill is universally superior. It checks whether incorporating methods from KKKKhazix `human-writing` into a profile-based writing system preserves material integrity and natural progression.

### Method

- Three topics and a seven-dimension rubric were fixed before reading any draft.
- Standalone `human-writing` and the integrated skill received the same source material without external research.
- A/B identities were hidden during the first editorial review.
- After recurring issues appeared in the initial integration, only fixed subheadings, repeated explanations, and internal-report tone were addressed. The C group was reviewed with the same rubric.
- Every final article was checked by both upstream `check_prose.py` and integrated `lint_ai_style.py --profile social-longform --strict`.

### Results

| Topic | Initial integration | Standalone | Final integration |
|---|---:|---:|---:|
| GPT-5.6 long-running task | 91 | 93 | **96** |
| Seven UI Skills | 83 | 86 | **89** |
| Profiles and universal gate | 91 | **95** | **95** |
| **Mean** | **88.3** | **91.3** | **93.3** |

The final integration retained the standalone skill's continuity and editing discipline while restoring a clearer author position. Remaining weaknesses include internal terminology in system-design topics and an ending that could stop earlier in the UI Skills article.

### Limitations

- The test covers three Chinese nonfiction WeChat-style articles only.
- Scores are editorial judgments under a fixed rubric, not statistical evidence.
- Zero hard checker failures do not prove external factual correctness.
- Type cards exist for READMEs, PRDs, tutorials, and Xiaohongshu, but this article test does not establish equal gains for those formats.

See [the paired samples](../examples/evaluation/README.md).
