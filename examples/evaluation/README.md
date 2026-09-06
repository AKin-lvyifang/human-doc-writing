# 对照样稿 / Paired evaluation samples

这里保留 v1.0–v1.2 的四组历史与回归样稿，旧稿没有被新稿覆盖；它们不代表 v2.0.0 的写作效果或现行规则。

- `human-writing/`：历史独立 KKKKhazix `human-writing` 1.0.0 输出。
- `human-doc-writing/`：第一次逐段反馈后的 v1.1 回归稿，主要删除自问自答和点题金句。
- `human-doc-writing-v1.1-overcorrected/`：第二轮暴露问题的 v1.1 稿。三篇均为 12 段，且都低于约定的 1,200 汉字下界。
- `human-doc-writing-v1.2/`：v1.2 修订稿。写前正向起稿，初稿后再终审，并核对材料覆盖、篇幅和批量结构。

议题分别是 GPT-5.6 长任务、七个 UI Skills 的总入口，以及画像系统和统一人味门禁。前两个议题继续使用原始材料。v1.2 第三个议题加入了第二轮真实反馈与已核验的上游 1.1.0 更新，因此它是修复效果样稿，不是严格的同材料盲测。评分方法与边界见 [评测说明](../../docs/evaluation.md)。

---

This directory retains four historical and regression groups from v1.0–v1.2. New samples do not overwrite earlier ones. They do not establish v2.0.0 writing quality or current rules.

- `human-writing/`: historical standalone KKKKhazix `human-writing` 1.0.0 output.
- `human-doc-writing/`: v1.1 regression samples after the first line-by-line review, mainly removing self-questioning and punchlines.
- `human-doc-writing-v1.1-overcorrected/`: the second v1.1 group that exposed the new regression. All three articles had 12 paragraphs and missed the 1,200-character floor.
- `human-doc-writing-v1.2/`: the v1.2 revision, with positive drafting before post-draft review plus material-coverage, length, and batch-shape checks.

The topics cover a GPT-5.6 long-running task, the entry point for seven UI Skills, and the relationship between personal profiles and a universal human-voice gate. The first two v1.2 articles keep the original facts. The third also incorporates the second reader review and the verified upstream 1.1.0 update, so it is a repair sample rather than a strict same-material blind comparison. See [the evaluation notes](../../docs/evaluation.md) for methodology and limitations.
