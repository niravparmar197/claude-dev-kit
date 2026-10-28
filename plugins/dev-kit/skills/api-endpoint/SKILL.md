---
name: api-endpoint
description: Build one NestJS API endpoint - module, controller, service, DTO validation with class-validator, tenant filter from the auth context, tests and Swagger docs. Use when the user types /api-endpoint, or when a task adds or changes a NestJS endpoint.
argument-hint: "<METHOD /path - what it does>"
---

# `/api-endpoint` — one NestJS endpoint

Endpoint: $ARGUMENTS

## Step 1: Find the pattern
- Read `CLAUDE.md` for the auth guard, how the tenant id reaches the request (e.g. `@CurrentUser()` / `req.user.tenantId`), the ORM (TypeORM/Prisma) and the error format.
- Open 1–2 existing endpoints of the same kind (list, get-by-id, create, update, delete) and copy their layout. Don't invent a new pattern.

## Step 2: Contract
Write down before coding: method + path, who may call it (public / user / admin), request DTO with limits (lengths, ranges, enums, max page size), response DTO, status codes.

## Step 3: Tests first
Write the tests (or launch the `test-writer` agent) and see them fail:
- Service unit test (`*.service.spec.ts`) for the logic.
- e2e test (`test/*.e2e-spec.ts` with supertest) covering: success; invalid body → 400; no token → 401; wrong role → 403; another tenant's id → 404; not found → 404.

## Step 4: Build it
- **Module**: add to the existing feature module, or `nest g module|controller|service <name>` and register it in the parent module.
- **DTO**: `class-validator` decorators on every field (`@IsString() @MaxLength()`, `@IsUUID()`, `@IsInt() @Min() @Max()`, `@IsEnum()`), nested objects with `@ValidateNested() @Type()`. Rely on the global `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })`; add it in `main.ts` if missing.
- **Controller**: thin. `@UseGuards(...)` and role decorators as the project does; `ParseUUIDPipe` on id params; no business logic.
- **Service**: take the tenant id from the auth context only, and put it in **every** `where` (find, update, delete, count, query builder). Missing rows → `NotFoundException`, including rows owned by another tenant.
- **Response**: return a response DTO or selected fields; never password hashes, tokens or internal fields.
- **Swagger**: `@ApiTags`, `@ApiOperation`, `@ApiBearerAuth`, `@ApiResponse` for each status code, `@ApiProperty` on DTO fields.

## Step 5: Check
Run the tests, `npm run lint` and `npx tsc --noEmit`. Then launch `security-reviewer` and `tenant-auditor` with the changed files from `git diff --name-only`. Fix every blocker.
