# nirav-tools

A Claude Code plugin marketplace with one plugin, **dev-kit**: Nirav's full-stack workflow of sprint skills, reviewer agents and safety hooks.

## Install

```
/plugin marketplace add niravparmar197/claude-dev-kit
/plugin install dev-kit@nirav-tools
```

Local checkout: `/plugin marketplace add F:/projects/claude-dev-kit`.

The hooks run `python`, so Python must be on PATH. `format.py` uses the project's local Prettier and `ruff`/`black` if they're installed.

## Skills

Plugin skills are namespaced, e.g. `/dev-kit:prd`. Plain `/prd` also works when no other skill has that name.

| Skill | What it does |
|---|---|
| `prd` | Asks questions, then writes `sprints/vN/PRD.md` and `TASKS.md` with small tasks |
| `dev` | Picks the next task, writes tests first, then the code, runs scans, commits |
| `walkthrough` | Writes `sprints/vN/WALKTHROUGH.md` from git history |
| `api-endpoint` | Builds a NestJS endpoint: module, DTO validation, tenant filter, tests, Swagger |
| `db-change` | Updates the entity, generates the migration with the CLI, shows the SQL, waits for your OK |
| `ship` | Runs all checks and the reviewers, then opens a PR through GitHub MCP |
| `new-project` | Sets up a new repo from its `templates/` folder |

## Agents

| Agent | Tools |
|---|---|
| `test-writer` | Read, Edit, Write, Bash |
| `code-reviewer` | Read, Grep, Glob |
| `security-reviewer` | Read, Grep, Glob |
| `tenant-auditor` | Read, Grep, Glob |

The reviewers can't run git, so pass them the changed files (`git diff --name-only`).

## Hooks

- `scripts/protect.py` (PreToolUse) blocks destructive commands (`rm -rf`, force push, `reset --hard`, `DROP TABLE`, `terraform destroy`, …), edits to existing migrations (new ones are allowed), `.env` (except `.env.example`), keys and tfstate, and shell reads of secret files.
- `scripts/format.py` (PostToolUse) formats each file after Claude edits it.

Add protected paths for one project in `.claude/dev-kit.json`:

```json
{ "protect": [{ "re": "(^|/)src/generated/", "why": "generated code" },
              { "re": "(^|/)secrets/", "why": "secrets", "secret": true }] }
```

## Releasing

Raise `version` in `plugins/dev-kit/.claude-plugin/plugin.json` each time you release a change. Users only get an update when the version goes up.
