#!/usr/bin/env bash
set -euo pipefail

archive_url="${HUMAN_DOC_ARCHIVE_URL:-https://github.com/AKin-lvyifang/human-doc-writing/archive/refs/heads/main.tar.gz}"
skills_root="${CODEX_HOME:-$HOME/.codex}/skills"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest)
      if [[ $# -lt 2 ]]; then
        echo "--dest requires a skills directory" >&2
        exit 2
      fi
      skills_root="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: install.sh [--dest /path/to/skills]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

target="${skills_root%/}/human-doc-writing"
if [[ -e "$target" ]]; then
  echo "Install stopped: $target already exists." >&2
  echo "Move or back up the existing directory, then run the installer again." >&2
  exit 1
fi

mkdir -p "$skills_root"
temp_base="${TMPDIR:-/tmp}"
install_tmp="$(mktemp -d "${temp_base%/}/human-doc-writing-install.XXXXXX")"

case "$install_tmp" in
  */human-doc-writing-install.*) ;;
  *)
    echo "Unexpected temporary path: $install_tmp" >&2
    exit 1
    ;;
esac

cleanup() {
  rm -rf -- "$install_tmp"
}
trap cleanup EXIT

curl -fsSL "$archive_url" -o "$install_tmp/archive.tar.gz"
tar -xzf "$install_tmp/archive.tar.gz" -C "$install_tmp"
source_dir="$install_tmp/human-doc-writing-main/human-doc-writing"

if [[ ! -f "$source_dir/SKILL.md" ]]; then
  echo "Downloaded archive does not contain human-doc-writing/SKILL.md." >&2
  exit 1
fi

cp -R "$source_dir" "$target"

echo "Installed human-doc-writing to $target"
echo "Start a new Codex turn, then invoke it with \$human-doc-writing."
