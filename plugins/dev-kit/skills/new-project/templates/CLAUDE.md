# {{project name}}
Stack: Next.js + NestJS + PostgreSQL + FastAPI (AI service)

## Rules
- TypeScript strict. No `any`.
- Validate all API input (class-validator in NestJS, Pydantic in FastAPI).
- Every query filters by tenant_id.
- Every feature ships with tests.

## Commands
- Frontend: cd frontend && npm run dev / npm test
- Backend: cd backend && npm run start:dev / npm test
- AI: cd ai-service && uvicorn main:app --reload / pytest

## Do not touch
- .env files, migrations/ (ask first)
