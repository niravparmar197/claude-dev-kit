---
name: new-project
description: Set up a new repo for the dev-kit workflow from the templates folder - asks for the project name, stack and app folders, then writes CLAUDE.md, .claude/settings.json and .gitignore. Use when the user types /new-project or starts a new repo.
argument-hint: "[project name]"
disable-model-invocation: true
---

# `/new-project` — set up a repo for dev-kit

Project: $ARGUMENTS

Templates live in `${CLAUDE_SKILL_DIR}/templates/`.

## Step 1: Look before asking
- If `CLAUDE.md`, `.claude/settings.json` or `.gitignore` already exist, read them. **Never overwrite**: show what you'd add and merge only with the user's OK.
- If code already exists, detect what you can (stack from `package.json` / `pyproject.toml`, app folders, real scripts) and only ask about the rest.

## Step 2: Ask
Use AskUserQuestion (one call, up to 4 questions) for what you couldn't detect:
1. **Project name**
2. **Stack**: default is the template's (Next.js + NestJS + PostgreSQL + FastAPI). Offer smaller combinations too.
3. **App folders**: default `frontend/`, `backend/`, `ai-service/`.
4. **Multi-tenant?** If no, the tenant_id rule becomes "every query on user-owned data filters by user id".

## Step 3: Write the files
Fill each template from the answers. Drop lines for apps or tools the project doesn't have; leave no `{{…}}` placeholders.
- `templates/CLAUDE.md` → `CLAUDE.md`: name, stack, rules and per-folder commands.
- `templates/settings.json` → `.claude/settings.json`: keep the marketplaces and plugins. Change `permissions.allow` to the project's real test/lint/build commands (drop `pytest` without Python, drop npm entries without Node).
- `templates/gitignore` → `.gitignore`: drop the Node or Python block if unused.
- Optional: if the repo has generated code or secret folders beyond `.env`, copy `templates/dev-kit.json` → `.claude/dev-kit.json` with those paths so the protect hook guards them.
- `git init` if the folder isn't a repo yet. Don't commit.

## Step 4: Report
List the files written and tell the user to read each one and fix anything wrong. Then the next steps:
1. `/dev-kit:prd` to plan the first sprint, then `/dev-kit:dev` for Task 1 (project setup).
2. Once code exists: ask "Recommend automations for this project", run `/graphify .`, and add a short `CLAUDE.md` in each app folder.
3. Per-project extras that stay in this repo's `.claude/`, not the plugin: `skills/ui-design/SKILL.md` (colors and components), `agents/e2e-tester.md` (this app's pages and test data), an optional Stop hook `check.py` (the fast check command), an optional `.mcp.json` with a read-only Postgres server for the dev database.
4. Commit the setup: `git add CLAUDE.md .claude .gitignore` and `git commit -m "chore: Claude Code setup"`.
