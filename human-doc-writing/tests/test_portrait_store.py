"""Exercise portrait coexistence and reversible maintenance in temporary storage."""

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "portrait_store", Path(__file__).resolve().parents[1] / "scripts" / "portrait_store.py"
)
store = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(store)


class PortraitStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.user = self.root / "user"
        self.patch = patch.object(store, "user_root", return_value=self.user)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.source = self.root / "draft.md"

    def command(self, *arguments):
        args = store.build_parser().parse_args(arguments)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = args.func(args)
        return code, output.getvalue()

    def save(self, content, name=None, kind="positive", type_id="essay"):
        self.source.write_text(content, encoding="utf-8")
        arguments = ["save", "--type", type_id, "--kind", kind, "--profile", str(self.source)]
        if name is not None:
            arguments += ["--name", name]
        return self.command(*arguments)

    def snapshot(self):
        if not self.user.exists():
            return {}
        return {
            str(path.relative_to(self.user)): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.user.rglob("*") if path.is_file()
        }

    def test_multiple_voices_keep_default_and_negative_independent(self):
        self.save("# 默认\n- 来源：旧画像\n")
        self.save("# 温厚观察\n", "warm-observation")
        self.save("# 锋利评论\n", "sharp-commentary")
        self.save("# 反例\n", "warm-observation", "negative")
        code, listing = self.command("list")
        self.assertEqual(code, 0)
        for relative in (
            "portraits/essay.md",
            "portraits/essay/warm-observation.md",
            "portraits/essay/sharp-commentary.md",
            "anti-patterns/essay/warm-observation.md",
        ):
            self.assertIn(relative, listing)
            self.assertTrue((self.user / relative).is_file())
        self.assertEqual(self.command("show", "--type", "essay")[1].strip(), "# 默认\n- 来源：旧画像")
        self.assertEqual(
            self.command("show", "--type", "essay", "--name", "sharp-commentary")[1].strip(),
            "# 锋利评论",
        )

    def test_same_time_updates_keep_each_backup_and_its_name(self):
        with patch.object(store, "timestamp", return_value="same-time"):
            self.save("# 第一版\n", "warm")
            self.save("# 第二版\n", "warm")
            self.save("# 第三版\n", "warm")
            self.save("# 另一写法旧版\n", "sharp")
            self.save("# 另一写法新版\n", "sharp")
        backups = sorted((self.user / "history").glob("*.md"))
        self.assertEqual(len(backups), 3)
        self.assertEqual(
            {path.read_text(encoding="utf-8") for path in backups},
            {"# 第一版\n", "# 第二版\n", "# 另一写法旧版\n"},
        )
        self.assertEqual(len([path for path in backups if "-warm-" in path.name]), 2)
        self.assertEqual(len([path for path in backups if "-sharp-" in path.name]), 1)

    def test_list_is_read_only_even_without_an_existing_index(self):
        self.command("list")
        self.assertFalse(self.user.exists())
        self.save("# 默认\n", type_id="wechat-article")
        self.save("# 新写法\n", "calm", type_id="narrative")
        (self.user / "portrait-index.md").unlink()
        before = self.snapshot()
        _, listing = self.command("list")
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.user / "portrait-index.md").exists())
        self.assertIn("portraits/narrative/calm.md", listing)

    def test_reset_leaves_default_available_and_backup_can_restore_variant(self):
        self.save("# 默认\n")
        self.save("# 要恢复的写法\n", "warm")
        self.save("# 保留的写法\n", "sharp")
        self.command("reset", "--type", "essay", "--name", "warm")
        self.assertEqual(self.command("show", "--type", "essay", "--name", "warm")[0], 1)
        self.assertEqual(self.command("show", "--type", "essay")[1].strip(), "# 默认")
        self.assertTrue((self.user / "portraits/essay/sharp.md").is_file())
        self.assertNotIn("portraits/essay/warm.md", (self.user / "portrait-index.md").read_text())
        backup = next((self.user / "history").glob("essay-positive-warm-*.md"))
        self.command("save", "--type", "essay", "--name", "warm", "--profile", str(backup))
        self.assertEqual(
            self.command("show", "--type", "essay", "--name", "warm")[1].strip(),
            "# 要恢复的写法",
        )
        self.command("reset", "--type", "essay")
        self.assertFalse((self.user / "portraits/essay.md").exists())
        self.assertTrue((self.user / "portraits/essay/warm.md").exists())

    def test_invalid_names_fail_before_storage_changes(self):
        self.source.write_text("# 待保存\n", encoding="utf-8")
        for name in ("../escape", "/tmp/escape", "a/b", "a\\b", "..", "", "Upper", "a b"):
            for command in ("save", "show", "reset"):
                arguments = [command, "--type", "commentary", "--name", name]
                if command == "save":
                    arguments += ["--profile", str(self.source)]
                with self.subTest(name=name, command=command):
                    with self.assertRaises(ValueError):
                        self.command(*arguments)
        self.assertFalse(self.user.exists())

    def test_symlink_cannot_redirect_variant_write_outside_user_storage(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.user / "portraits").mkdir(parents=True)
        (self.user / "portraits/essay").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.save("# 不应写出\n", "warm")
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
