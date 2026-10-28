---
name: db-change
description: Make one database schema change - update the entity, generate a new migration with the ORM CLI, show the SQL and wait for the user's OK before running it. Use when the user types /db-change, or when a task adds or changes tables, columns or indexes.
argument-hint: "<what changes, e.g. add orders.cancelled_at>"
---

# `/db-change` — one schema change, with your OK

Change: $ARGUMENTS

## Step 1: Find the tooling
- Read `CLAUDE.md` and `package.json` scripts for the ORM and its migration commands (TypeORM `migration:generate` / `migration:run`, Prisma `migrate dev --create-only` / `migrate deploy`, …).
- Read the newest 2–3 migrations to copy naming and style.
- Existing migrations are **immutable**. The protect hook blocks edits to them; generating a new file is fine.

## Step 2: Update the entity
Edit the entity/schema file. Multi-tenant tables get the tenant id column and an index that starts with it.

## Step 3: Generate the migration
Run the project's generate command with a clear name, e.g.
```bash
npm run typeorm -- migration:generate src/database/migrations/AddOrderCancelledAt -d src/database/data-source.ts
# or
npx prisma migrate dev --create-only --name add_order_cancelled_at
```
Never hand-write a migration the CLI can generate. Read the generated file and remove anything unrelated the generator picked up.

## Step 4: Show the SQL and wait
Show the user:
- the migration file path and the full SQL (`up` and `down`)
- whether it locks or rewrites a big table, and if existing rows need a backfill
- the risks: `NOT NULL` without a default, dropped columns, renames (old code still running during deploy)

Then **stop and ask for OK**. Do not run the migration until the user says yes.

## Step 5: Run it (after OK)
Run the migration against the local/dev database only, then run the tests that touch the changed tables. Never run it against a shared or production database, and never reset/drop/revert; the protect hook blocks the common ones.

## Step 6: Report
The migration file, what it changed, the test results, and any follow-up migration a later sprint must do (e.g. make a column `NOT NULL` after a backfill).
