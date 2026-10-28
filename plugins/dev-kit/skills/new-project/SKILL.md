---
name: new-project
description: Set up a new repo for the dev-kit workflow from the templates folder - CLAUDE.md, .claude settings, protected paths and the sprints folder. Use when the user types /new-project or starts a new repo.
argument-hint: "[short description of the project]"
disable-model-invocation: true
---

# `/new-project` — set up a repo for dev-kit

Project: $ARGUMENTS

Templates live in `${CLAUDE_SKILL_DIR}/templates/`.

## Step 1: Look before asking
- If `CLAUDE.md`, `.claude/settings.json` or `.claude/dev-kit.json` already exist, read them. **Never overwrite**: show what you'd add and merge only with the user's OK.
- Existing code: detect the stack from `package.json` / `pyproject.toml` / etc., the real lint/typecheck/test/build scripts, the layout, the ORM and migrations folder, the auth setup, and whether data is per tenant or per user.
- Empty repo: ask (AskUserQuestion, at most 4 questions): stack, single- or multi-tenant, database/ORM, deploy target.

## Step 2: Write the files
Fill each template from what you found. Delete lines that don't apply rather than leaving `<…>` placeholders.
- `templates/CLAUDE.md` → `CLAUDE.md`
- `templates/settings.json` → `.claude/settings.json` (deny reads of the repo's real secret files; merge into an existing file)
- `templates/dev-kit.json` → `.claude/dev-kit.json` (extra protected paths: generated code, vendored dirs, secrets folders)
- Create an empty `sprints/` folder with a `.gitkeep`. `/prd` creates `sprints/v1/` itself.
- `git init` if the folder isn't a repo yet.

## Step 3: Check
Run each command you wrote into `CLAUDE.md` once. Fix or remove any that don't work, and tell the user which ones you couldn't verify.

## Step 4: Report
List the files written. The next step is `/prd`.
