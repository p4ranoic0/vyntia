# Contributing to VYNTIA

## Quick start

```bash
# 1. Clone and set up Python venv
cd D:/VYNTIA
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
pip install -e "apps/api[dev]"

# 2. Install Node dependencies
cd apps/web && npm install && cd ../..

# 3. Start dev servers (two terminals)
cd apps/api && python manage.py runserver --settings=vyntia.settings.development
cd apps/web && npm run dev
```

## Branch + PR conventions

| What | Convention |
|---|---|
| Branch name | `vyntia/L<N>.<sub>-short-description` or `vyntia/<feature-slug>` |
| Commit prefix | `chore(L<N>):`, `feat(<module>):`, `fix(<module>):`, `docs(<scope>):` |
| Merge style | `--no-ff` to preserve layer history |
| PR granularity | One PR per sub-layer or bounded change. No big-bang PRs |

## Backend (Django)

- **Settings module**: `vyntia.settings.{development,testing,production}`
- **Run server**: `python manage.py runserver --settings=vyntia.settings.development`
- **Run tests**: `cd apps/api && pytest` (161 pass / 8 pre-existing fail / 3 skip baseline)
- **Django check**: `python manage.py check --settings=vyntia.settings.development`
- **New migration**: `python manage.py makemigrations <app> && python manage.py migrate`
- **DB**: `bd_vyntia` on localhost:5432. Override via `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` env vars.

### Architecture rules

- FK cross-app: `ForeignKey('employees.Employee', on_delete=CASCADE)` — string lazy always
- No imports across bounded-context apps — use service public APIs
- `apps/core` is utility-only, zero domain model dependencies
- PKs are UUID (`id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`)
- Audit fields: `created_at`, `updated_at`, `created_by`, `updated_by`
- Domain HR vocabulary stays in Spanish: `estado_empleado`, `tipo_documento`, `nombres`, etc.
- Platform state fields: `status`, `is_active`
- All responses through `APIResponse` from `apps.core.responses`

### App structure template

```
apps/api/apps/<bounded_context>/
├── __init__.py
├── apps.py              # AppConfig
├── models/
│   ├── __init__.py      # re-exports all models
│   └── <model>.py
├── serializers.py
├── views/
│   ├── __init__.py
│   └── <viewset>.py
├── urls.py
├── services/
│   ├── __init__.py
│   └── <service>.py
├── tests/
│   ├── __init__.py
│   └── test_<x>.py
└── migrations/
```

## Frontend (React + Vite)

- **Dev server**: `cd apps/web && npm run dev` (proxies `/api/*` → `http://127.0.0.1:8000`)
- **Build**: `npm run build`
- **TypeScript check**: `npx tsc --noEmit -p tsconfig.app.json`
- **Tests**: `npm test -- --run` (7 vitest tests)
- **Lint**: `npm run lint`

### Feature structure template

```
apps/web/src/features/<bounded_context>/
├── index.ts             # public re-exports
├── components/
│   └── index.ts
├── hooks/
│   └── use<Feature>.ts
├── pages/
│   ├── index.ts
│   └── <Page>.tsx
└── services/
    └── <feature>Service.ts
```

### API conventions

- API client: `import { apiClient } from '@/shared/api/api'`
- All responses unwrapped: `response.data?.data?.results ?? response.data?.results ?? response.data`
- React Query v5 for data fetching; no Redux/Zustand
- Forms: `react-hook-form` + `zod`
- UI primitives: Shadcn/ui at `@/shared/ui/`
- UUIDs for all entity IDs — `id: string`, never `id: number`

## Test philosophy

- **Backend**: Every new view action needs at least one happy-path test in `apps/api/tests/`
- **Frontend**: Feature-level vitest tests for hooks and services
- Do NOT mock the database in backend tests — tests hit `bd_vyntia_test` via Django test runner
- Preserve baselines: pytest 161/8/3, vitest 7

## Common pitfalls

| Pitfall | Fix |
|---|---|
| `UnicodeDecodeError` from `psycopg2.connect` on `runserver` | `DB_PASSWORD` contains non-ASCII char — use `manage.py check` for local code verification |
| `replace_all` renames both field reads AND query param strings | Use per-file context — `?estado=activo` query params stay Spanish |
| Django template multi-line tags break | All `{% %}` and `{{ }}` must open and close on the same line |
| `app_rrhh` references in code | There should be zero — grep: `grep -ri "app_rrhh" apps/` |
