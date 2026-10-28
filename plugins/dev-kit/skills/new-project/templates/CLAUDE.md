# <Project name>

<One line: what it is and who uses it.>

## Stack
<Language + version, framework · database + ORM · cache/queue · auth · test tools · CI/deploy>

## Layout
- `<src dir>` — <what lives here>
- `<tests dir>` — <unit vs integration/e2e>
- `sprints/vN/` — `PRD.md`, `TASKS.md`, `WALKTHROUGH.md` per sprint

## Data isolation
- Boundary: <tenant (org/workspace id) | user | both>
- Trusted id comes from: <JWT claim / session / subdomain>, never from the request body or path
- Enforced by: <scoped repository / RLS / middleware>

## Rules
- Every query on owned data is filtered by the trusted tenant/user id.
- Validate all input with <validator>; errors use <shared error format>.
- Schema changes = a NEW migration (`<generate command>`). Never edit an old one.
- Match the surrounding code style.

## Commands
- Lint: `<cmd>` · Typecheck: `<cmd>`
- Unit tests: `<cmd>` · Integration/e2e: `<cmd>`
- Build: `<cmd>` · Dependency audit: `<cmd>`

## Do not touch
- Existing files in `<migrations dir>`
- `.env*` (except `.env.example`), keys, `*.tfstate`
- <generated code dirs>
- Done tasks in `sprints/*/TASKS.md`

## Workflow
`/prd` plan a sprint → `/dev` one task per run (tests first) → `/ship` checks, reviewers (`code-reviewer`, `security-reviewer`, `tenant-auditor`) and PR → `/walkthrough` at sprint end.
