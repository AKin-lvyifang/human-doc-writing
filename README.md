# human-doc-writing

[English](README_EN.md) | 简体中文

面向 Codex 的中文写作与编辑 Skill，当前版本 **2.0.0**。根据材料、读者和场合选择文体与文风，写文章、产品文档、教程、PRD、README 和发布说明，也能从样文学习个人写作偏好。

一份通知需要让人迅速找到安排，人物小品可以在细节处停留，评论需要讲清判断依据。这个 Skill 把这些阅读需要带进取材、结构、节奏和语言选择，让文学表达用在合适的地方。

## 开始使用

macOS 或 Linux 用户可以运行：

```bash
curl -fsSL https://raw.githubusercontent.com/AKin-lvyifang/human-doc-writing/main/install.sh | bash
```

脚本从 `main` 安装，默认位置是 `${CODEX_HOME:-$HOME/.codex}/skills/human-doc-writing`。需要 Bash、`curl` 和 `tar`；Skill 的辅助脚本使用 Python 3 标准库，无需安装第三方 Python 包。可以先查看 [install.sh](install.sh)。

已有同名目录时，安装脚本会停止，不覆盖旧文件。已有用户请按下方升级说明处理。安装后新开一个 Codex 任务，确认 Skill 列表中出现 `human-doc-writing`，然后直接提供材料：

```text
$human-doc-writing
根据这份材料写一篇面向普通读者的公众号短评，约 800 字。
判断清楚、有分寸，文风由你根据材料选择，直接交正文。
```

安装到自定义 Skills 目录：

```bash
curl -fsSL https://raw.githubusercontent.com/AKin-lvyifang/human-doc-writing/main/install.sh \
  | bash -s -- --dest "$HOME/.agents/skills"
```

需要固定版本或手动安装时，到 [v2.0.0 Release](https://github.com/AKin-lvyifang/human-doc-writing/releases/tag/v2.0.0) 下载 `human-doc-writing-2.0.0.zip` 和 `SHA256SUMS.txt`。解压后的 Skill 位于 `human-doc-writing-2.0.0/human-doc-writing/`，其中包含 `SKILL.md`。将这个内层目录放入你的 Skills 目录；不要把整个仓库目录当作 Skill 安装。

## 2.0.0 怎样写作

### 文体和发表平台分开判断

先判断读者需要理解什么、感受什么或完成什么，再选择表达方式。公众号、小红书、知乎和博客提供阅读场合，不再单独决定文章的声音。

内置九种实质文体：

| 文体 | 重点 |
|---|---|
| 说明文 | 概念、关系、例子与适用条件 |
| 产品文档 | 产品用途、能力边界与上手路径 |
| 教程 | 前置条件、操作步骤、成功标志与故障处理 |
| PRD | 目标、范围、行为规则与验收标准 |
| GitHub README | 项目用途、最短上手路径与使用限制 |
| GitHub Release | 用户可见变化、兼容性与升级动作 |
| 观点评论 | 判断、依据、取舍与结论边界 |
| 纪实叙述 | 有来源的人物、动作、关系与变化 |
| 随笔散文 | 具体观察、联想、节奏与余味 |

文体卡的必要内容始终保留。例如，有个人画像的教程仍须让读者判断操作是否成功。完整小说、虚构故事、对白和剧本不属于本 Skill 的默认创作范围。

### 根据文章选择文风

创作指导覆盖观察、作者位置、材料的揭示顺序、详略、叙述距离和语言节奏。说明可以明净耐心，人物稿可以温厚细腻，评论可以鲜明而有分寸。

设问、比喻、排比、重复、留白和照应都可按文章需要使用；检查其作用与准确性，不把某种标点或句式一概判成 AI 腔。文学表达仍受材料约束，不能为真实人物补造心理、对白或现场细节。

要求清楚时直接写，不例行发送确认卡或要求选择风格菜单。局部改稿只处理指定部分及其衔接，保留未要求改动的内容。

### 从读者位置编辑

编辑先保留有效的观察、声音与表达，再修理解断点、事实越界、无效重复和失去分寸的修辞。按具体问题回改，不规定固定终审遍数。段落可以承担理解、叙事、感受或阅读停顿，不要求每段都新增事实。

## 写作、改稿与画像学习

写作时提供材料、读者、用途和必要限制即可，普通文风选择可以交给 Skill。

**局部改稿：**

```text
$human-doc-writing
只改第二段，让第一次接触这个产品的人能读懂。
保留其余文字，不添加原稿没有的功能。
```

**只在本次借鉴：**

```text
$human-doc-writing
分析这篇随笔的叙述距离和节奏，本次改稿参考这种写法，不保存画像。
```

**保存一种写法：**

```text
$human-doc-writing
学习这篇人物稿怎样选择细节、安排节奏，保存为 narrative 类型下的
warm-observation 画像。保留已有画像，不替换默认写法。
```

一篇完整、可读的样文即可建立画像。画像记录“创作选择 → 读者效果 → 适用条件”，不把原作者的身份、经历、观点或独特句子带入新稿。只分析或本次参考时，不保存长期偏好；明确要求学习、记住或更新时才保存。

同一文体可以保留多份具名画像，写作时选择最匹配的一份。旧平台画像与默认画像继续可读，但只在声明的文体、用途和场合匹配时使用。当前明确要求优先，不能把一次反馈变成所有文章的禁令。

在已安装的 Skill 目录中，也可查看画像：

```bash
python3 scripts/portrait_store.py list
python3 scripts/portrait_store.py show --type narrative --name warm-observation
```

第二条命令适用于已保存该画像的情况。具名画像存于 `user/portraits/<type_id>/<name>.md`，反例存于 `user/anti-patterns/<type_id>/<name>.md`；旧默认画像路径继续兼容。替换或移除画像前会保留备份，具体用法见 [画像学习](human-doc-writing/references/portrait-ingestion.md)。

## 检查器能做什么

在 Skill 目录中，可检查一份 Markdown 或纯文本成稿：

```bash
python3 scripts/lint_ai_style.py /absolute/path/article.md --strict
```

`--strict` 仅在发现内部过程标注残留，或显式设置的最低汉字数未满足时返回失败。需要最低汉字数时加 `--min-han N`。`universal`、`social-longform`、`wechat-longform` 保留为兼容提示档位，风格提示不阻断，也不要求清零。

多稿比较脚本 `compare_draft_shapes.py` 可提示可能共用的结构，改写比较脚本 `de_ai_diff.py` 可显示文字变化。相同段数和改写比例不代表写作质量；脚本通过也不能证明事实可信、文章自然或已有文学性。

**自动流程的行为变化：** 旧命令行参数继续兼容，但风格命中和批量结构提醒不再让 `--strict` 返回失败。原先据此拒收稿件的自动流程需要调整，改由读者理解、文体要求与实际表达效果判断是否需要回改。

## 从旧版升级

**先备份整个旧 Skill，完整保留原有 `user/`。**

1. 将当前 `human-doc-writing` 目录备份到 Skills 搜索目录之外，保留可恢复的完整副本。
2. 下载并解压 [v2.0.0 发布包](https://github.com/AKin-lvyifang/human-doc-writing/releases/tag/v2.0.0)，用附件 `SHA256SUMS.txt` 核对下载文件。
3. 打开解压后的 `human-doc-writing-2.0.0/human-doc-writing/`，替换旧 Skill 的所有公开文件与目录，包括 `SKILL.md`、`VERSION`、`references/`、`scripts/`、`agents/` 和 `tests/`。唯一保留的是原 `user/` 全部内容，包括偏好、画像、索引和历史；不要用发布包的用户目录覆盖它。
4. 新开一个 Codex 任务，确认 Skill 可用，并查看原画像是否仍能列出。

安装脚本不提供原地升级。公开包不预装任何人的个人画像；没有画像时，直接使用文体卡和通用创作指导。

## 进一步阅读

- [Skill 完整说明](human-doc-writing/SKILL.md)
- [文体与场合路由](human-doc-writing/references/type-router.md)
- [文风选择](human-doc-writing/references/style-selection.md)与[创作方法](human-doc-writing/references/writing-craft.md)
- [画像模板](templates/portrait-template.md)与[画像示例](templates/portrait-example.md)
- [必要时的简短澄清](templates/brief-template.md)

[历史评测说明](docs/evaluation.md)与[历史对照样稿](examples/evaluation/README.md)保留了早期版本的探索和纠偏。那些评分、样稿和检查结果属于旧版证据，不能证明 2.0.0 的写作效果，也不能据此声称新版在所有题材上更好。

## 来源与许可

本项目的材料核对、作者位置、社媒起稿、句段节奏与部分检查设计，吸收并改编自 [KKKKhazix/human-writing](https://github.com/KKKKhazix/human-writing) 1.1.0，参考基线提交为 `4fda173f3fef7fb808f3eba991eeb2528ea4b189`。当前版本在此基础上加入文体与文风分离、文学表达选择和读者编辑。

这是独立衍生项目，不代表上游官方，也不要求模仿其作者的固定人设或口吻。项目采用 [MIT License](LICENSE)，上游署名和许可文本保留于 [NOTICE.md](NOTICE.md) 与 [来源和许可证](human-doc-writing/references/human-writing-origin.md)。
