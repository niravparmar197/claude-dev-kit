---
name: ship
description: Ship the current branch - run all checks and the reviewer agents, then push and open a pull request through the GitHub MCP server. Use when the user types /ship.
argument-hint: "[base branch, default: main]"
disable-model-invocation: true
---

# `/ship` — branch to pull request

Base branch (optional): $ARGUMENTS

## Step 1: Preflight
- `git status`: if there are uncommitted changes, stop and ask the user what to do with them.
- Don't ship from the base branch itself. Base = the argument, else `main`.
- `git fetch` and check the branch is up to date with the base. If not, tell the user and stop; don't rebase or merge on your own.
- `git log --oneline <base>..HEAD` and `git diff --name-only <base>...HEAD` to see what will ship.

## Step 2: Run all checks
Run every check the project has (from `CLAUDE.md` and `package.json` scripts):
```bash
npm run lint
npx tsc --noEmit
npm test
npm run test:e2e        # if it exists
npm run build
semgrep scan --config auto src/ --quiet
npm audit --omit=dev --audit-level=high
```
Any failure → stop and report. Do not ship red.

## Step 3: Review
Launch `code-reviewer`, `security-reviewer` and `tenant-auditor` in parallel, giving each the changed-file list from Step 1 and the sprint's `sprints/vN/TASKS.md`. A blocker or critical/high finding → stop, report it, and suggest `/dev` to fix it. Don't fix it inside `/ship`.

## Step 4: Push and open the PR
- Show the user the PR title and body and **ask before pushing**.
- `git push -u origin <branch>` (never force).
- Open the PR with the GitHub MCP server's create-pull-request tool (if it isn't connected, tell the user and fall back to `gh pr create` only if they agree). Title: `<type>(vN): <summary>`. Body:
  - **What**: 2–4 lines; link `sprints/vN/PRD.md`
  - **Tasks**: the completed tasks from `sprints/vN/TASKS.md`
  - **Tests**: suites added and how to run them
  - **Checks & review**: results of Step 2 and each reviewer's verdict
  - **Migrations / rollout**: migrations, env vars, deploy order (or "none")

## Step 5: Report
The PR URL, the checks that ran, and anything the user must do before merging.
