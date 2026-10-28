"""PreToolUse: block destructive shell commands, edits to protected paths, and
shell reads of secrets (permissions.deny only covers the Read tool).

Exit code 2 blocks the tool call and shows the reason to Claude.

Projects can add rules in .claude/dev-kit.json:
    {"protect": [{"re": "(^|/)generated/", "why": "generated code"},
                 {"re": "(^|/)secrets/", "why": "secrets", "secret": true}]}
"""
import json
import os
import re
import sys

# Paths Claude must never edit, overwrite or delete.
# "new_ok": a Write that creates a brand-new file here is allowed.
PROTECTED = [
    {
        "re": r"(^|/)(migrations|db/migrate|alembic/versions)/",
        "why": "existing migrations are immutable; add a new one",
        "new_ok": True,
    },
    {
        "re": r"(^|/)\.env(\.[^/]*)?$",
        "why": ".env files hold secrets",
        "allow": r"\.env\.(example|sample|template)$",
        "secret": True,
    },
    {"re": r"(^|/)keys(-[^/]+)?/", "why": "signing keys", "secret": True},
    {"re": r"\.(pem|key|p12|pfx)$", "why": "private keys / certificates", "secret": True},
    {"re": r"\.tfstate(\.|$)", "why": "Terraform state"},
    {"re": r"(^|/)\.git/", "why": "git internals"},
]

# Shell commands that are destructive or hard to undo.
DANGEROUS = [
    (r"\brm\s+(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r)\b", "rm -rf", re.I),
    (r"\bRemove-Item\b[^|;]*-Recurse", "recursive Remove-Item", re.I),
    (r"\bgit\s+push\b[^|;]*(\s--force\b|\s-f\b|--force-with-lease)", "force push", 0),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard", 0),
    (r"\bgit\s+clean\s+-[a-z]*f", "git clean -f", 0),
    (r"\bgit\s+(checkout|restore)\s+(--\s+)?\.(\s|$)", "discarding all local changes", 0),
    (r"\bgit\s+branch\s+-D\b", "force-deleting a branch", 0),
    (r"\bterraform\b[^|;]*\s(destroy\b|apply\b[^|;]*-auto-approve)", "terraform destroy / auto-approved apply", 0),
    (r"\bmigration:revert\b|\bschema:drop\b|\bmigrate\s+reset\b|\bdb:drop\b", "reverting/dropping DB schema", 0),
    (r"\b(DROP|TRUNCATE)\s+(DATABASE|TABLE|SCHEMA)\b", "DROP/TRUNCATE", re.I),
    (r"\bdocker\s+(compose\b[^|;]*\bdown\b[^|;]*(-v\b|--volumes)|volume\s+(rm|prune)|system\s+prune)", "deleting docker volumes/data", 0),
    (r"\bFLUSHALL\b|\bFLUSHDB\b", "wiping Redis", re.I),
    (r"\bkubectl\s+delete\s+(ns|namespace)\b", "deleting a k8s namespace", 0),
]

# Shell commands that write to or delete a path.
WRITES_PATH = re.compile(
    r"(>|>>|\btee\b|\brm\b|\bmv\b|\bcp\b|\bsed\s+-i|Set-Content|Out-File|Add-Content"
    r"|Remove-Item|Move-Item|Copy-Item|Clear-Content)",
    re.I,
)

# Redirections that write nowhere (2>&1, >/dev/null, >$null) and must not count as a write.
HARMLESS_REDIRECT = re.compile(r"\d*>&\d|\d*>>?\s*(/dev/null|\$null|NUL)\b", re.I)

# Shell commands that print a file's contents.
READS_PATH = re.compile(
    r"(<|\b(cat|type|more|less|head|tail|grep|egrep|rg|awk|sed|strings|xxd|od|base64"
    r"|openssl|findstr|Get-Content|gc|Select-String|sls)\b)",
    re.I,
)

TOKEN_SPLIT = re.compile(r"[\s\"'`=;|&()<>,]+")


def block(reason):
    sys.stderr.write(
        f"Blocked by dev-kit protect hook: {reason}. "
        "Ask the user to do this manually if it is really needed.\n"
    )
    sys.exit(2)


def load_rules(root):
    rules = list(PROTECTED)
    try:
        with open(os.path.join(root, ".claude", "dev-kit.json"), encoding="utf-8") as f:
            rules += json.load(f).get("protect", [])
    except (OSError, ValueError):
        pass
    return rules


def protected_rule(rules, p, secret_only=False):
    norm = p.replace("\\", "/")
    for rule in rules:
        if secret_only and not rule.get("secret"):
            continue
        if re.search(rule["re"], norm) and not (
            rule.get("allow") and re.search(rule["allow"], norm)
        ):
            return rule
    return None


def main():
    try:
        data = json.loads(sys.stdin.read().lstrip("﻿"))
    except ValueError:
        return
    tool = data.get("tool_name")
    ti = data.get("tool_input") or {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    rules = load_rules(root)

    if tool in ("Bash", "PowerShell"):
        cmd = str(ti.get("command", ""))
        for pattern, why, flags in DANGEROUS:
            if re.search(pattern, cmd, flags):
                block(f"destructive command ({why})")
        tokens = [t for t in TOKEN_SPLIT.split(cmd) if t]
        if WRITES_PATH.search(HARMLESS_REDIRECT.sub("", cmd)):
            for token in tokens:
                rule = protected_rule(rules, token)
                if rule:
                    block(f"command writes to protected path {token} ({rule['why']})")
        if READS_PATH.search(cmd):
            for token in tokens:
                rule = protected_rule(rules, token, secret_only=True)
                if rule:
                    block(f"command reads secret file {token} ({rule['why']})")
        return

    file = ti.get("file_path") or ti.get("notebook_path")
    if not file:
        return
    rule = protected_rule(rules, file)
    if not rule:
        return
    is_new = tool == "Write" and not os.path.exists(os.path.join(root, file))
    if not (rule.get("new_ok") and is_new):
        block(f"{file} is protected ({rule['why']})")


if __name__ == "__main__":
    main()
