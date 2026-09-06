"""Regression checks for the editing tools' user-visible CLI contract."""

from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LINT = ROOT / "scripts" / "lint_ai_style.py"
SHAPES = ROOT / "scripts" / "compare_draft_shapes.py"
PROFILES = ("universal", "social-longform", "wechat-longform")


class EditingCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".lint-tests-", dir=ROOT / "tests")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def write(self, name, text):
        path = self.folder / name
        path.write_text(text, encoding="utf-8")
        return path

    def run_cli(self, script, *args):
        return subprocess.run(
            [sys.executable, str(script), *map(str, args)],
            text=True, capture_output=True, check=False,
        )

    def lint(self, text, *args):
        return self.run_cli(LINT, self.write("draft.md", text), *args)

    def test_literary_and_literal_expressions_are_advisory_in_every_profile(self):
        text = (
            '他说：“电梯里的抓手松了，明天更换。”\n\n'
            '不是电池坏了，而是接线松了。\n\n'
            '你会留下来吗？\n\n'
            '他说要走，他说会回来，他说让我等着。\n\n'
            '说白了，值得注意的是：这场降温，把仓库变成了他的灯塔——他暂时不走了。'
        )
        for profile in PROFILES:
            with self.subTest(profile=profile):
                result = self.lint(text, "--profile", profile, "--strict")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("阻断项=0", result.stdout)
                self.assertNotIn("必须修改", result.stdout)
                self.assertNotIn("改成不改变含义的间接表述", result.stdout)

    def test_high_warning_score_does_not_fail_strict_mode(self):
        result = self.lint(
            "\n\n".join(["本文将说明这件事。"] * 8), "--strict"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        score = re.search(r"提示分=(\d+)", result.stdout)
        self.assertIsNotNone(score)
        self.assertGreaterEqual(int(score.group(1)), 6)
        self.assertIn("阻断项=0", result.stdout)

    def test_internal_comments_fail_even_when_multiline_or_without_prose(self):
        examples = (
            "正文在这里。\n<!-- source: 合同第三条 -->",
            "正文在这里。\n<!--\nsource:\n合同第三条\n-->",
            "正文在这里。\n<!--\n    source: 合同第三条\n-->",
            "<!-- source: 合同第三条 -->",
        )
        for text in examples:
            with self.subTest(text=text):
                result = self.lint(text, "--strict")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("[过程标注残留]", result.stdout)
        result = self.lint("正文在这里。\n<!-- source: 合同第三条 -->", "--strict")
        self.assertIn("第 2 行", result.stdout)

    def test_code_examples_do_not_trigger_internal_marker_failures(self):
        examples = (
            "```html\n<!-- source: 合同第三条 -->\n```",
            "~~~html\n<!--\nsource: 合同第三条\n-->\n~~~",
            "````markdown\n```html\n<!-- source: 合同第三条 -->\n```\n````",
            "示例为 `<!-- source: 合同第三条 -->`。",
            "示例为 ``<!-- source: `合同第三条` -->``。",
            "代码如下。\n\n    <!-- source: 合同第三条 -->\n",
        )
        for text in examples:
            with self.subTest(text=text):
                result = self.lint(text, "--profile", "wechat-longform", "--strict")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn("[过程标注残留]", result.stdout)

    def test_prd_pending_decisions_are_not_internal_residue(self):
        result = self.lint(
            "# 发布决策\n\n- 待核实：旧版本用户是否需要迁移。\n"
            "- TODO：由产品负责人确认发布日期。\n- 材料编号：MAT-P01。",
            "--strict",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("[过程标注残留]", result.stdout)

    def test_time_links_and_direct_quote_colons_are_not_punctuation_warnings(self):
        result = self.lint(
            '末班车每天晚上 21:30 从北门出发。他说：“明天见。”\n\n'
            '资料见 [来源](https://example.test/page?kind=note)。\n\n'
            '[来源]: https://example.test/page?kind=note\n\n'
            '代码是 `time = "21:30"`。',
            "--profile", "wechat-longform", "--strict",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for label in ("[中文冒号]", "[英文冒号]", "[引语冒号]", "[提问语境]"):
            self.assertNotIn(label, result.stdout)

    def test_explicit_minimum_fails_below_and_passes_at_boundary(self):
        below = self.lint("天地玄黄", "--strict", "--min-han", 5)
        self.assertEqual(below.returncode, 1, below.stdout + below.stderr)
        self.assertIn("[篇幅不足]", below.stdout)
        at_boundary = self.lint("天地玄黄", "--strict", "--min-han", 4)
        self.assertEqual(at_boundary.returncode, 0, at_boundary.stdout + at_boundary.stderr)
        code_only = self.lint("`天地玄黄`", "--strict", "--min-han", 1)
        self.assertEqual(code_only.returncode, 1, code_only.stdout + code_only.stderr)

    def test_input_errors_return_two(self):
        invalid = self.folder / "invalid.md"
        invalid.write_bytes(b"\xff")
        cases = (
            (LINT, self.folder / "missing.md"),
            (LINT, invalid),
            (LINT, self.write("valid.md", "天地玄黄"), "--min-han", 0),
            (SHAPES, self.folder / "one.md", self.folder / "two.md", self.folder / "three.md"),
        )
        for args in cases:
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_matching_paragraph_counts_only_produce_advice(self):
        trajectories = (
            (10, 100, 40, 70, 25, 180, 60, 30),
            (150, 25, 60, 10, 80, 35, 200, 45),
            (30, 75, 160, 20, 50, 90, 15, 110),
        )
        paths = [
            self.write(f"draft-{index}.md", "\n\n".join("文" * size for size in sizes))
            for index, sizes in enumerate(trajectories)
        ]
        result = self.run_cli(SHAPES, *paths, "--strict")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("[段落数相同]", result.stdout)
        self.assertIn("不影响退出状态", result.stdout)


if __name__ == "__main__":
    unittest.main()
