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
- 第二轮复读发现 v1.1 三篇过度纠偏稿都恰好为 12 段，语气偏产品说明，且三篇均低于约定的 1,200 汉字下界。
- v1.2 先由隔离执行者只读取原始 brief 生成前向稿，再根据本次用户明确指出的漏网句和说明书口吻做一次定向编辑。它同样不是新的盲测评分组。
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

### v1.2 再纠偏

v1.1 把详细禁令带进了第一稿，模型从开头就追求安全。结果是表演性句子少了，普通判断、过程和后果也被一起压短。三篇都长成 12 段，第二篇只有 1047 个汉字。

v1.2 将写作分成三个时点。写前只核事实、材料和篇幅契约；社媒第一稿读取正向普通白话规则，沿动作、限制和结果展开；完整初稿以后才加载七遍终审。写前材料覆盖表会标出必须保留的过程，终审后逐项核对。谈 Skill、系统或方法时，正文优先保留真实安装、使用、失败、取舍与修改，不再让组件职责接管全文。

检查器补上 `恰恰` 与“这份”组合的点题句漏网，并新增最低汉字数、说明书口吻、段落过齐和批量段落数同构信号。检查器只负责发现形状，过程是否真实仍由人工阅读判断。

### 当前三方对照

| 样稿组 | 三篇汉字数 | 正文段数 | 1,200 汉字门 | 批量检查 |
|---|---|---|---|---|
| 历史独立版 | 1204 / 1223 / 1249 | 12 / 13 / 12 | 三篇通过 | 未发现同构 |
| v1.1 过度纠偏稿 | 1149 / 1047 / 1167 | 12 / 12 / 12 | 三篇失败 | 命中段落数同构 |
| v1.2 修订稿 | 1215 / 1213 / 1230 | 11 / 9 / 9 | 三篇通过 | 未发现同构 |

按原七维量表做非盲自评，v1.2 与历史独立版处在同一档。独立版前两篇的个别句子仍更自然，v1.2 第一篇和第二篇还带少量方法说明感；v1.2 第三篇加入了真实的 12 段、1047 字失败和加载顺序调整，已经不再只解释画像与门禁各自负责什么。v1.2 的优势主要在篇幅纪律、材料覆盖和跨文体边界，不是每一句都比独立版更有活人感。

### 边界

- 评测只覆盖三篇中文公众号现实观点稿。
- 分数来自固定量表下的编辑判断，不代表统计学显著性。
- 93.3 是 v1.0 的历史分数，不能再用来证明融合版更自然或更好。
- v1.1 与 v1.2 修订样稿都是针对已知失败的编辑回归，仍需要后续真实公众号任务和用户阅读继续验收。
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
- A second reread found that all three over-corrected v1.1 drafts had exactly 12 paragraphs, read like product explanations, and missed the 1,200-character floor.
- Version 1.2 started with forward drafts produced from the raw brief in isolation, followed by one targeted edit for the exact missed phrase and remaining manual tone identified by the user. It is also not a new blind scoring group.
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

### Version 1.2 correction

Version 1.1 let detailed prohibitions influence the first draft. The model optimized for safety from the opening paragraph, removing ordinary judgment, process, and consequence together with performative phrasing. All three drafts ended at 12 paragraphs, and the second contained only 1,047 Chinese characters.

Version 1.2 separates three moments. Before drafting, it checks facts, material, and the length contract. A social first draft then follows positive plain-prose guidance through actions, constraints, and results. Seven-pass revision loads only after the full draft exists. A private material-coverage list marks process details that must survive revision. Articles about skills, systems, or methods now follow real installation, use, failure, trade-off, and modification instead of letting component responsibilities take over the prose.

The checker now catches the previously missed `恰恰` plus `这份` punchline pattern and adds minimum-character, manual-tone, overly-even-paragraph, and batch paragraph-count signals. These signals detect shape only; human review still decides whether the process is real and useful.

### Current three-way comparison

| Sample group | Chinese characters | Body paragraphs | 1,200-character gate | Batch check |
|---|---|---|---|---|
| Historical standalone | 1204 / 1223 / 1249 | 12 / 13 / 12 | All pass | No shared shape detected |
| Over-corrected v1.1 drafts | 1149 / 1047 / 1167 | 12 / 12 / 12 | All fail | Identical paragraph count detected |
| Revised v1.2 drafts | 1215 / 1213 / 1230 | 11 / 9 / 9 | All pass | No shared shape detected |

On a non-blind reread with the original seven-dimension rubric, v1.2 and the historical standalone samples are in the same tier. Some sentences in the first two standalone articles remain more natural, while the first two v1.2 articles retain a small amount of method-explanation tone. The third v1.2 article includes the real 12-paragraph and 1,047-character failure plus the workflow-order change, so it no longer merely assigns responsibilities to profiles and the quality gate. V1.2's clearer gains are length discipline, material coverage, and cross-format boundaries, not universal sentence-level superiority.

### Limitations

- The test covers three Chinese nonfiction WeChat-style articles only.
- Scores are editorial judgments under a fixed rubric, not statistical evidence.
- The 93.3 score belongs to v1.0 and is no longer evidence that the integration reads more naturally or is better.
- Version 1.1 and 1.2 samples are targeted regressions for known failures and still require validation in future real WeChat writing tasks.
- Zero hard checker failures do not prove external factual correctness.
- Type cards exist for READMEs, PRDs, tutorials, and Xiaohongshu, but this article test does not establish equal gains for those formats.

See [the paired samples](../examples/evaluation/README.md).
