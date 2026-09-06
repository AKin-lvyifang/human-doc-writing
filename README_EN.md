# human-doc-writing

English | [简体中文](README.md)

A Chinese writing and editing skill for Codex, currently **2.0.0**. It chooses genre and voice from the material, audience, and occasion. Use it for articles, product documentation, tutorials, PRDs, READMEs, and release notes, or teach it your writing preferences through sample texts.

A notice should make arrangements easy to find. A character sketch can linger on a detail. A commentary needs a clear basis for its judgment. This skill brings those reader needs into the selection of material, structure, pacing, and language, using literary expression where it serves the piece.

## Get started

On macOS or Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/AKin-lvyifang/human-doc-writing/main/install.sh | bash
```

The script installs from `main` to `${CODEX_HOME:-$HOME/.codex}/skills/human-doc-writing` by default. Installation requires Bash, `curl`, and `tar`. The skill's helper scripts use the Python 3 standard library, with no third-party Python packages. You can inspect [install.sh](install.sh) first.

If the destination already exists, the installer stops without overwriting it. Existing users should follow the upgrade steps below. After installation, start a new Codex task, confirm that `human-doc-writing` appears in the skill list, and provide your material:

```text
$human-doc-writing
Write a Chinese WeChat commentary of about 800 characters from this material
for general readers. Make the judgment clear and measured. Choose a suitable
voice from the material and return the article directly.
```

For a custom skills directory:

```bash
curl -fsSL https://raw.githubusercontent.com/AKin-lvyifang/human-doc-writing/main/install.sh \
  | bash -s -- --dest "$HOME/.agents/skills"
```

For a fixed version or manual installation, download `human-doc-writing-2.0.0.zip` and `SHA256SUMS.txt` from the [v2.0.0 release](https://github.com/AKin-lvyifang/human-doc-writing/releases/tag/v2.0.0). The extracted skill is at `human-doc-writing-2.0.0/human-doc-writing/`, containing `SKILL.md`. Place that inner directory in your skills directory. Install the skill subdirectory, not the entire repository.

## How 2.0.0 approaches writing

### Genre and publishing platform are separate choices

The skill first considers what the reader needs to understand, feel, or accomplish, then chooses how to express it. WeChat, Xiaohongshu, Zhihu, and blogs provide a reading context; they do not prescribe one voice.

Nine substantive genres are included:

| Genre | Focus |
|---|---|
| Explainer | Concepts, relationships, examples, and conditions |
| Product documentation | Purpose, capability boundaries, and getting started |
| Tutorial | Prerequisites, steps, signs of success, and troubleshooting |
| PRD | Goals, scope, behavior, and acceptance criteria |
| GitHub README | Project purpose, a short path to use, and limitations |
| GitHub release | User-visible changes, compatibility, and upgrade steps |
| Commentary | Judgment, evidence, tradeoffs, and limits |
| Factual narrative | Sourced people, actions, relationships, and change |
| Essay | Concrete observations, associations, rhythm, and resonance |

The essential requirements of each genre always apply. For example, a tutorial must still explain how to recognize success when a personal profile is in use. Full novels, fictional stories, dialogue, and scripts are outside this skill's default creative scope.

### Voice follows the piece

The writing guidance covers observation, the author's position, the order in which material is revealed, emphasis, narrative distance, and sentence rhythm. An explanation can be clear and patient, a character sketch warm and attentive, and a commentary pointed but measured.

Questions, metaphor, parallelism, repetition, pauses, and callbacks may all be used when they contribute. The skill checks their purpose and accuracy rather than treating a punctuation mark or sentence pattern as inherently AI-like. Literary expression remains bounded by the material: it cannot invent thoughts, dialogue, or scene details for real people.

When the request is clear, writing starts directly, without a routine confirmation card or style menu. A local edit covers only the requested passage and its connections, preserving text outside the requested change.

### Edit from the reader's position

Editing protects effective observations, voice, and expression before repairing gaps in understanding, unsupported claims, redundant passages, or excessive rhetoric. Revisions address specific problems, without a fixed number of review passes. A paragraph may support understanding, narrative, feeling, or a useful reading pause; it need not introduce a new fact every time.

## Writing, revision, and profile learning

Provide the material, audience, purpose, and necessary constraints. You can leave ordinary voice choices to the skill.

**Make a local edit:**

```text
$human-doc-writing
Revise only the second paragraph so a first-time reader can understand it.
Keep all other text and do not add capabilities absent from the draft.
```

**Borrow a style for this task only:**

```text
$human-doc-writing
Analyze this essay's narrative distance and pacing. Use those choices for
this revision only; do not save a profile.
```

**Save a particular approach:**

```text
$human-doc-writing
Learn how this character sketch selects details and controls pacing.
Save it as warm-observation under narrative. Keep existing profiles and
do not replace the default.
```

One complete, readable sample can establish a profile. Profiles record “creative choice → reader effect → conditions for use.” They do not transfer the original author's identity, experiences, opinions, or distinctive sentences into a new piece. Analysis and one-time references stay local to the task; persistent preferences are saved only when explicitly requested.

Multiple named profiles can coexist within a genre, with the closest match selected for each task. Legacy platform profiles and default profiles remain readable, but apply only when their declared genre, purpose, and occasion match. Current instructions take precedence; a single piece of feedback does not become a rule for all writing.

From the installed skill directory, you can also inspect profiles:

```bash
python3 scripts/portrait_store.py list
python3 scripts/portrait_store.py show --type narrative --name warm-observation
```

The second command assumes that profile has been saved. Named profiles live at `user/portraits/<type_id>/<name>.md`; negative profiles live at `user/anti-patterns/<type_id>/<name>.md`. Legacy default paths remain supported. A backup is kept before a profile is replaced or removed. See [profile learning](human-doc-writing/references/portrait-ingestion.md) for details.

## What the checkers do

From the skill directory, check a complete Markdown or plain-text draft with:

```bash
python3 scripts/lint_ai_style.py /absolute/path/article.md --strict
```

`--strict` returns failure only for internal process annotations left in the text or an unmet, explicitly configured minimum Chinese-character count. Add `--min-han N` when such a minimum applies. `universal`, `social-longform`, and `wechat-longform` remain available as compatible advisory profiles. Style warnings do not block delivery and need not be reduced to zero.

`compare_draft_shapes.py` can flag potentially shared structures across drafts, and `de_ai_diff.py` can show how much text changed. Matching paragraph counts and rewrite percentages do not measure writing quality. Passing a script does not establish factual accuracy, natural voice, or literary merit.

**Behavior change for automated workflows:** legacy command-line options remain compatible, but style matches and batch-structure warnings no longer make `--strict` fail. Workflows that used those failures to reject drafts need adjustment. Decisions to revise should follow reader understanding, genre requirements, and the actual effect of the writing.

## Upgrade from an earlier version

**Back up the entire old skill and preserve its complete `user/` directory.**

1. Copy the current `human-doc-writing` directory to a backup location outside the directories searched for skills. Keep this complete copy for recovery.
2. Download and extract the [v2.0.0 release package](https://github.com/AKin-lvyifang/human-doc-writing/releases/tag/v2.0.0), checking the download against the attached `SHA256SUMS.txt`.
3. Open the extracted `human-doc-writing-2.0.0/human-doc-writing/` directory and replace all public files and directories in the old skill, including `SKILL.md`, `VERSION`, `references/`, `scripts/`, `agents/`, and `tests/`. The sole exception is the complete existing `user/`, including preferences, profiles, the index, and history. Do not overwrite it with the package's user directory.
4. Start a new Codex task, confirm that the skill is available, and check that your existing profiles can still be listed.

The installer does not perform in-place upgrades. The public package includes no active personal profiles. Without a profile, the skill uses genre cards and general writing guidance directly.

## Further reading

- [Complete skill instructions](human-doc-writing/SKILL.md)
- [Genre and platform routing](human-doc-writing/references/type-router.md)
- [Voice selection](human-doc-writing/references/style-selection.md) and [writing craft](human-doc-writing/references/writing-craft.md)
- [Profile template](templates/portrait-template.md) and [profile example](templates/portrait-example.md)
- [Brief clarification when needed](templates/brief-template.md)

The [historical evaluation notes](docs/evaluation.md) and [paired historical samples](examples/evaluation/README.md) document experiments and corrections in earlier versions. Those scores, drafts, and checks are evidence about old versions. They do not establish the writing quality of 2.0.0 or show that it is better for every subject.

## Origin and license

The project's material checks, author position, social-prose drafting, sentence and paragraph rhythm, and parts of the checker design incorporate and adapt [KKKKhazix/human-writing](https://github.com/KKKKhazix/human-writing) 1.1.0, using commit `4fda173f3fef7fb808f3eba991eeb2528ea4b189` as the reference baseline. The current version builds on that work with separate genre and voice choices, literary expression, and reader-oriented editing.

This is an independent derivative project, not an official upstream release. It does not require imitation of the original author's fixed persona or voice. The project uses the [MIT License](LICENSE); upstream attribution and license text are retained in [NOTICE.md](NOTICE.md) and [the origin and license notice](human-doc-writing/references/human-writing-origin.md).
