"""PostToolUse: format the file Claude just edited or wrote with the project's
own formatter. Never blocks: a formatting failure is printed and ignored.

Uses the first formatter that applies:
  .ts/.tsx/.js/.jsx/.json/.css/.md/.yml...  -> local Prettier (node_modules)
  .py                                       -> ruff format, else black
  .go                                       -> gofmt
  .rs                                       -> rustfmt
A formatter that isn't installed is skipped silently.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys

PRETTIER_EXT = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".css", ".scss",
    ".html", ".md", ".yml", ".yaml", ".vue", ".svelte",
}


def prettier(root):
    cli = os.path.join(root, "node_modules", "prettier", "bin", "prettier.cjs")
    node = shutil.which("node")
    if os.path.exists(cli) and node:
        return [node, cli, "--write", "--log-level", "warn"]
    return None


def command_for(root, ext):
    if ext in PRETTIER_EXT:
        return prettier(root)
    if ext == ".py":
        if shutil.which("ruff"):
            return ["ruff", "format", "--quiet"]
        if shutil.which("black"):
            return ["black", "--quiet"]
        if importlib.util.find_spec("black"):
            return [sys.executable, "-m", "black", "--quiet"]
    if ext == ".go" and shutil.which("gofmt"):
        return ["gofmt", "-w"]
    if ext == ".rs" and shutil.which("rustfmt"):
        return ["rustfmt", "--edition", "2021"]
    return None


def main():
    try:
        data = json.loads(sys.stdin.read().lstrip("﻿"))
        file = (data.get("tool_input") or {}).get("file_path")
        if not file or not os.path.exists(file):
            return

        root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
        rel = os.path.relpath(os.path.abspath(file), root)
        parts = rel.replace("\\", "/").split("/")
        if rel.startswith("..") or os.path.isabs(rel) or "node_modules" in parts:
            return

        cmd = command_for(root, os.path.splitext(file)[1].lower())
        if not cmd:
            return
        res = subprocess.run(cmd + [file], cwd=root, capture_output=True, text=True, timeout=25)
        if res.returncode != 0:
            sys.stderr.write(f"format skipped {rel}: {res.stderr or res.stdout}")
    except Exception as err:  # never block an edit because formatting failed
        sys.stderr.write(f"format hook: {err}\n")


if __name__ == "__main__":
    main()
