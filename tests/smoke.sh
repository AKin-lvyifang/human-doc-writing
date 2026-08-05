#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
temp_base="${TMPDIR:-/tmp}"
smoke_tmp="$(mktemp -d "${temp_base%/}/human-doc-writing-smoke.XXXXXX")"

case "$smoke_tmp" in
  */human-doc-writing-smoke.*) ;;
  *)
    echo "Unexpected temporary path: $smoke_tmp" >&2
    exit 1
    ;;
esac

cleanup() {
  rm -rf -- "$smoke_tmp"
}
trap cleanup EXIT

archive_root="$smoke_tmp/archive/human-doc-writing-main"
archive_path="$smoke_tmp/human-doc-writing-main.tar.gz"
skills_root="$smoke_tmp/skills"
target="$skills_root/human-doc-writing"

mkdir -p "$archive_root"
cp -R "$repo_root/human-doc-writing" "$archive_root/human-doc-writing"
tar -czf "$archive_path" -C "$smoke_tmp/archive" human-doc-writing-main

HUMAN_DOC_ARCHIVE_URL="file://$archive_path" \
  bash "$repo_root/install.sh" --dest "$skills_root"

test -f "$target/SKILL.md"
test "$(tr -d '\r\n' < "$target/VERSION")" = "1.2.0"
test -f "$target/agents/openai.yaml"
test -x "$target/scripts/lint_ai_style.py"
test -x "$target/scripts/compare_draft_shapes.py"

python3 "$target/scripts/lint_ai_style.py" \
  "$repo_root/tests/fixtures/wechat-plain-good.md" \
  --profile wechat-longform --strict >/dev/null

if bad_output="$(python3 "$target/scripts/lint_ai_style.py" \
  "$repo_root/tests/fixtures/wechat-performative-bad.md" \
  --profile wechat-longform --strict 2>&1)"; then
  echo "WeChat negative fixture unexpectedly passed." >&2
  exit 1
fi

case "$bad_output" in
  *"[公众号问号]"*"[表演性点题]"*"恰好"*"[表演性点题]"*"恰恰"*) ;;
  *)
    echo "WeChat negative fixture did not trigger the expected gates." >&2
    echo "$bad_output" >&2
    exit 1
    ;;
esac

manual_output="$(python3 "$target/scripts/lint_ai_style.py" \
  "$repo_root/tests/fixtures/wechat-manual-bad.md" \
  --profile wechat-longform 2>&1)"
case "$manual_output" in
  *"[说明书口吻]"*) ;;
  *)
    echo "Manual-tone fixture did not trigger the expected warning." >&2
    echo "$manual_output" >&2
    exit 1
    ;;
esac

even_output="$(python3 "$target/scripts/lint_ai_style.py" \
  "$repo_root/tests/fixtures/wechat-even-bad.md" \
  --profile wechat-longform 2>&1)"
case "$even_output" in
  *"[段落过齐]"*) ;;
  *)
    echo "Even-paragraph fixture did not trigger the expected warning." >&2
    echo "$even_output" >&2
    exit 1
    ;;
esac

if length_output="$(python3 "$target/scripts/lint_ai_style.py" \
  "$repo_root/tests/fixtures/wechat-plain-good.md" \
  --profile wechat-longform --min-han 1200 --strict 2>&1)"; then
  echo "Minimum-length fixture unexpectedly passed." >&2
  exit 1
fi
case "$length_output" in
  *"[篇幅不足]"*) ;;
  *)
    echo "Minimum-length fixture did not trigger the expected gate." >&2
    echo "$length_output" >&2
    exit 1
    ;;
esac

if batch_output="$(python3 "$target/scripts/compare_draft_shapes.py" \
  "$repo_root/tests/fixtures/batch-shape-a.md" \
  "$repo_root/tests/fixtures/batch-shape-b.md" \
  "$repo_root/tests/fixtures/batch-shape-c.md" \
  --strict 2>&1)"; then
  echo "Batch-shape negative fixtures unexpectedly passed." >&2
  exit 1
fi
case "$batch_output" in
  *"[段落数同构]"*) ;;
  *)
    echo "Batch-shape fixtures did not trigger the expected gate." >&2
    echo "$batch_output" >&2
    exit 1
    ;;
esac

touch "$target/.keep-existing"
if HUMAN_DOC_ARCHIVE_URL="file://$archive_path" \
  bash "$repo_root/install.sh" --dest "$skills_root" >/dev/null 2>&1; then
  echo "Installer unexpectedly overwrote an existing skill." >&2
  exit 1
fi
test -f "$target/.keep-existing"

echo "Installer smoke test passed."
