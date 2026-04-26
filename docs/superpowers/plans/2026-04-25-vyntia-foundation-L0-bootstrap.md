# VYNTIA Foundation L0 — Bootstrap Monorepo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganizar el repo en estructura monorepo (`apps/api/`, `apps/web/`, `packages/`, `docs/`) sin tocar código de aplicación. Resultado: ambas apps arrancan exactamente como antes, suite de tests verde, primer hito mergeable de la migración VYNTIA.

**Architecture:** Pura refactorización estructural usando `git mv`. Cero cambios a Python o TypeScript. Verificación: smoke tests al final (runserver, vite dev, pytest, vitest). El plan es 100% mecánico — si algo deja de funcionar es porque un import absoluto roto se filtró, no por lógica nueva.

**Tech Stack:** Bash + git + npm. No se introducen dependencias.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L0 — Bootstrap del monorepo"

**Pre-condiciones:**
- Estás dentro del repo nuevo VYNTIA (NO `D:\INTRANET\` original)
- Repo en estado limpio: `git status` no muestra cambios sin commitear (excepto este plan si vino del original)
- Python venv activo apuntando a Python 3.11+
- Node 20+ y npm instalados
- BD `bd_rrhh_intranet` (o equivalente) accesible para que `runserver` arranque

**Definition of Done global del plan:**
- [ ] `cd apps/api && python manage.py runserver` arranca sin errores
- [ ] `cd apps/api && pytest` retorna verde (0 fallos)
- [ ] `cd apps/web && npm install && npm run dev` arranca sin errores
- [ ] `cd apps/web && npm test` retorna verde
- [ ] `git log --oneline` muestra los commits L0 con prefijo `chore(L0):`
- [ ] `tree -L 2 -I node_modules` muestra estructura `apps/`, `packages/`, `docs/`, `scripts/`, `.github/`

---

## File Structure Overview

Cambios estructurales (no de contenido):

| Acción | Origen | Destino |
|---|---|---|
| Move | `back/` | `apps/api/` |
| Move | `front/` | `apps/web/` |
| Merge | `saas_rrhh/docs/*` | `docs/` (existente) |
| Create | — | `packages/.gitkeep` |
| Create | — | `scripts/.gitkeep` |
| Create | — | `.github/workflows/.gitkeep` |
| Create | — | `package.json` (raíz, npm workspaces) |
| Update | `.gitignore` | `.gitignore` (consolidado) |
| Update | `README.md` | `README.md` (placeholder VYNTIA) |

Archivos NO tocados en L0: cualquier `.py`, `.ts`, `.tsx`, settings de Django, configs de Vite. Eso es L1+.

---

## Task 1: Confirmar entorno y estado limpio

**Files:** ninguno (solo verificación)

- [ ] **Step 1: Confirmar working directory**

Run:
```bash
pwd
```

Expected: una ruta que **NO sea** `D:\INTRANET` (debe ser el nuevo repo VYNTIA — confirmar con el usuario antes de seguir).

Si estás en `D:\INTRANET`, **DETENTE** y pregunta al usuario dónde está el nuevo repo.

- [ ] **Step 2: Confirmar repo git limpio**

Run:
```bash
git status --short
```

Expected: salida vacía, o solo el archivo del plan/spec si vinieron copiados.

Si hay cambios sin commitear no relacionados, hacer commit o stash antes de seguir.

- [ ] **Step 3: Confirmar estructura inicial esperada**

Run:
```bash
ls
```

Expected output incluye: `back`, `front`, `saas_rrhh`, `docs`, `CLAUDE.md`, `README.md`.

Si falta `back/` o `front/`, el repo no es el correcto. Detente.

- [ ] **Step 4: Verificar ubicación del venv**

Run:
```bash
ls .venv/Scripts/python.exe 2>/dev/null && echo "OK: venv en raíz" || echo "FALTA: crear venv en raíz"
```

Expected: `OK: venv en raíz`. Si falta, crear:
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r back/requirements.txt
```

El venv debe estar en la raíz del repo (`<repo>/.venv/`), no dentro de `back/`. Es la convención asumida en el resto del plan.

- [ ] **Step 5: Crear branch para L0**

Run:
```bash
git checkout -b vyntia/L0-bootstrap
```

Expected: `Switched to a new branch 'vyntia/L0-bootstrap'`

---

## Task 2: Snapshot baseline — verificar que TODO funciona ANTES de tocar nada

**Files:** ninguno (solo verificación pre-L0)

- [ ] **Step 1: Activar venv (desde raíz del repo) y correr pytest baseline**

Run desde la raíz del repo:
```bash
source .venv/Scripts/activate  # Git Bash en Windows; usar .venv\Scripts\activate.bat en cmd
cd back
pytest -x --tb=short
```

Expected: número de tests pasados anotado (ej. `42 passed in 8.2s`). **Anota este número** — es el baseline.

Si hay tests fallando antes de L0, **NO sigas** — tu trabajo no debe comparar contra una baseline rota. Pregunta al usuario si esos fallos son aceptados.

- [ ] **Step 2: Verificar que runserver arranca en back/**

Run (en una terminal aparte si quieres):
```bash
python manage.py runserver --settings=config.settings.development 2>&1 | head -20
```

Expected: `Starting development server at http://127.0.0.1:8000/` aparece en menos de 10 segundos.

Mata el server con Ctrl+C después de confirmar.

- [ ] **Step 3: Snapshot frontend en front/**

Run:
```bash
cd ../front
npm install --silent 2>&1 | tail -5
npm test -- --run --reporter=basic 2>&1 | tail -20
```

Expected: instalación sin errores fatales, `npm test` corre y termina (verde o con fallos esperados — anotar resultado como baseline).

- [ ] **Step 4: Volver a raíz y commitear este plan + spec si no estaban**

Run:
```bash
cd ..
git status --short
git add docs/superpowers/
git commit -m "docs(L0): add bootstrap plan and design spec" || echo "Nothing to commit"
```

Expected: o se hace commit, o sale "Nothing to commit". Ambos OK.

---

## Task 3: Crear directorios top-level del monorepo

**Files:**
- Create: `apps/.gitkeep`
- Create: `packages/.gitkeep`
- Create: `scripts/.gitkeep`
- Create: `.github/workflows/.gitkeep`

- [ ] **Step 1: Crear directorios vacíos con `.gitkeep`**

Run:
```bash
mkdir -p apps packages scripts .github/workflows
touch apps/.gitkeep packages/.gitkeep scripts/.gitkeep .github/workflows/.gitkeep
ls -la apps packages scripts .github/workflows
```

Expected: cada directorio existe y contiene `.gitkeep`.

- [ ] **Step 2: Verificar git ve los .gitkeep**

Run:
```bash
git status --short
```

Expected:
```
?? .github/workflows/.gitkeep
?? apps/.gitkeep
?? packages/.gitkeep
?? scripts/.gitkeep
```

- [ ] **Step 3: Stage y commit**

Run:
```bash
git add apps/.gitkeep packages/.gitkeep scripts/.gitkeep .github/workflows/.gitkeep
git commit -m "chore(L0): create monorepo top-level directories"
```

Expected: `1 file changed, 0 insertions(+), 0 deletions(-)` x4 (gitkeeps son vacíos).

---

## Task 4: Mover `back/` a `apps/api/`

**Files:**
- Move: `back/` → `apps/api/`
- Delete: `apps/.gitkeep` (ya no necesario, hay contenido)

- [ ] **Step 1: Hacer el move con git**

Run:
```bash
git mv back apps/api
ls apps/
```

Expected: `apps/` ahora contiene `api` (con todo el contenido de back) y `.gitkeep`.

- [ ] **Step 2: Eliminar el .gitkeep redundante de apps/**

Run:
```bash
git rm apps/.gitkeep
```

Expected: `rm 'apps/.gitkeep'`

- [ ] **Step 3: Verificar que el move se registró**

Run:
```bash
git status --short | head -10
```

Expected: lista larga de `R  back/X -> apps/api/X` (renames). No deberían aparecer `??` (untracked) en `apps/api/`.

- [ ] **Step 4: Smoke test backend desde nueva ubicación**

Run:
```bash
cd apps/api
python manage.py check --settings=config.settings.development
```

Expected: `System check identified no issues (0 silenced).`

Si hay errores `ModuleNotFoundError` por paths absolutos, **anótalo** — eso violaría la promesa "L0 no toca código". Si pasa, retrocede el move y pregunta al usuario.

- [ ] **Step 5: Correr pytest desde nueva ubicación**

Run:
```bash
pytest -x --tb=short 2>&1 | tail -10
```

Expected: mismo número de tests verdes que en Task 2 Step 1 baseline.

- [ ] **Step 6: Volver a raíz y commit**

Run:
```bash
cd ../..
git commit -m "chore(L0): move back/ to apps/api/"
```

Expected: commit exitoso. `git log --stat -1 | head -5` muestra renames masivos.

---

## Task 5: Mover `front/` a `apps/web/`

**Files:**
- Move: `front/` → `apps/web/`

- [ ] **Step 1: Hacer el move con git**

Run:
```bash
git mv front apps/web
ls apps/
```

Expected: `apps/` ahora contiene `api` y `web`.

- [ ] **Step 2: Verificar que `node_modules/` no se commiteó**

Run:
```bash
git status --short | grep node_modules || echo "OK: no node_modules in git"
```

Expected: `OK: no node_modules in git` (debería estar en .gitignore desde antes).

Si aparece `node_modules` en git status, eso es un bug del .gitignore original — apuntar para Task 8.

- [ ] **Step 3: Smoke test frontend desde nueva ubicación**

Run:
```bash
cd apps/web
npm install --silent 2>&1 | tail -3
```

Expected: instalación termina sin errores fatales (warnings de versiones son OK).

- [ ] **Step 4: Correr build para validar imports**

Run:
```bash
npm run build 2>&1 | tail -15
```

Expected: `vite build` completa con `✓ built in Xs`.

Si hay errores de tipo o imports rotos, **detente** — debería ser idéntico a antes del move. Investiga.

- [ ] **Step 5: Correr tests vitest**

Run:
```bash
npm test -- --run --reporter=basic 2>&1 | tail -10
```

Expected: mismo resultado que el baseline en Task 2 Step 3.

- [ ] **Step 6: Volver a raíz y commit**

Run:
```bash
cd ../..
git commit -m "chore(L0): move front/ to apps/web/"
```

---

## Task 6: Mover `saas_rrhh/docs/*` a `docs/` (merge con docs/ existente)

**Files:**
- Move: `saas_rrhh/docs/00_MAESTRO_PROYECTO.md` → `docs/00_VYNTIA_MAESTRO.md` (rename a la vez)
- Move: `saas_rrhh/docs/arquitectura/` → `docs/arquitectura/`
- Move: `saas_rrhh/docs/comercial/` → `docs/comercial/`
- Move: `saas_rrhh/docs/modulos/` → `docs/modulos/`
- Move: `saas_rrhh/docs/normativa/` → `docs/normativa/`
- Delete: `saas_rrhh/` (queda vacío)

- [ ] **Step 1: Verificar contenido a mover**

Run:
```bash
ls saas_rrhh/docs/
ls docs/ | head -10
```

Expected: `saas_rrhh/docs/` contiene `00_MAESTRO_PROYECTO.md` + 4 subdirs. `docs/` contiene los .md legacy.

Confirmar que no hay nombres conflictivos (ningún archivo en `docs/` se llama igual que algo en `saas_rrhh/docs/`).

- [ ] **Step 2: Mover subdirectorios completos**

Run:
```bash
git mv saas_rrhh/docs/arquitectura docs/arquitectura
git mv saas_rrhh/docs/comercial docs/comercial
git mv saas_rrhh/docs/modulos docs/modulos
git mv saas_rrhh/docs/normativa docs/normativa
```

Expected: cada comando sin errores.

- [ ] **Step 3: Mover y renombrar el documento maestro**

Run:
```bash
git mv saas_rrhh/docs/00_MAESTRO_PROYECTO.md docs/00_VYNTIA_MAESTRO.md
```

Expected: `00_MAESTRO_PROYECTO.md` ya no existe; `docs/00_VYNTIA_MAESTRO.md` sí.

- [ ] **Step 4: Limpiar saas_rrhh/ vacío**

Run:
```bash
ls saas_rrhh/docs/ 2>&1 || echo "ya eliminado"
rmdir saas_rrhh/docs saas_rrhh 2>&1 || echo "ya limpio"
ls | grep -i saas_rrhh && echo "ERROR: aún existe" || echo "OK: removido"
```

Expected: `OK: removido`.

- [ ] **Step 5: Verificar estructura docs/**

Run:
```bash
ls docs/
```

Expected: incluye `00_VYNTIA_MAESTRO.md`, `arquitectura/`, `comercial/`, `modulos/`, `normativa/`, más los .md legacy preexistentes (CACHE-GUIDE.md, etc.) y `superpowers/`.

- [ ] **Step 6: Commit**

Run:
```bash
git add -A
git commit -m "chore(L0): consolidate saas_rrhh/docs into docs/ and rename maestro to VYNTIA"
```

---

## Task 7: Crear `package.json` raíz con npm workspaces

**Files:**
- Create: `package.json` (raíz)

- [ ] **Step 1: Verificar que no existe package.json en raíz**

Run:
```bash
ls package.json 2>&1
```

Expected: `ls: cannot access 'package.json': No such file or directory`

Si existe, leer su contenido y consultar al usuario antes de sobrescribir.

- [ ] **Step 2: Crear package.json raíz**

Crear archivo `package.json` en raíz con este contenido exacto:

```json
{
  "name": "vyntia",
  "version": "0.1.0",
  "private": true,
  "description": "VYNTIA - SaaS modular de gestión de RRHH para Perú",
  "workspaces": [
    "apps/web",
    "packages/*"
  ],
  "scripts": {
    "dev:web": "npm run dev --workspace=apps/web",
    "build:web": "npm run build --workspace=apps/web",
    "test:web": "npm test --workspace=apps/web",
    "lint:web": "npm run lint --workspace=apps/web"
  },
  "engines": {
    "node": ">=20.0.0",
    "npm": ">=10.0.0"
  }
}
```

- [ ] **Step 3: Verificar que npm reconoce workspaces**

Run:
```bash
npm ls --workspaces --depth=0 2>&1 | head -10
```

Expected: lista los workspaces detectados (al menos `apps/web`). No debe dar error.

- [ ] **Step 4: Verificar que `npm run dev:web` desde raíz funciona**

Run:
```bash
npm run dev:web 2>&1 &
DEV_PID=$!
sleep 8
kill $DEV_PID 2>/dev/null || true
```

Expected: en los 8 segundos aparece `VITE vX.X.X ready in Xms` y `Local: http://localhost:XXXX/`.

Si falla, revisar que `apps/web/package.json` tiene script `dev`.

- [ ] **Step 5: Commit**

Run:
```bash
git add package.json
git commit -m "chore(L0): add root package.json with npm workspaces"
```

---

## Task 8: Consolidar `.gitignore` raíz

**Files:**
- Modify: `.gitignore` (raíz)

- [ ] **Step 1: Leer .gitignore actual**

Run:
```bash
cat .gitignore | head -50
```

Anotar qué patrones ya existen.

- [ ] **Step 2: Reemplazar con .gitignore consolidado**

Sobrescribir `.gitignore` (raíz) con este contenido:

```gitignore
# === Python / Django (apps/api) ===
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/
ENV/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/
celerybeat-schedule
*.log

# Django
db.sqlite3
db.sqlite3-journal
local_settings.py
media/
staticfiles/

# === Node / React (apps/web) ===
node_modules/
dist/
build/
.next/
out/
coverage/
.vite/
*.tsbuildinfo

# === Testing ===
playwright-report/
test-results/
playwright/.cache/

# === IDEs ===
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# === Env / secrets ===
.env
.env.local
.env.*.local
*.pem
secrets/

# === Logs ===
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# === Build artifacts / OS ===
*.tmp
*.temp
.cache/

# === VYNTIA specific ===
apps/api/media/
apps/api/staticfiles/
apps/api/logs/
```

- [ ] **Step 3: Verificar que git no muestra archivos que deberían estar ignorados**

Run:
```bash
git status --short | grep -E "(node_modules|__pycache__|\.pyc$|\.venv|\.coverage)" && echo "WARN: hay archivos ignorables tracked" || echo "OK: gitignore está cumpliéndose"
```

Expected: `OK: gitignore está cumpliéndose`

Si hay archivos tracked que deberían ser ignorados, ejecutar `git rm --cached <path>` para cada uno antes del commit.

- [ ] **Step 4: Commit**

Run:
```bash
git add .gitignore
git commit -m "chore(L0): consolidate root .gitignore for monorepo"
```

---

## Task 9: README placeholder VYNTIA

**Files:**
- Modify: `README.md` (raíz)

- [ ] **Step 1: Verificar README actual**

Run:
```bash
cat README.md | head -20
```

Anotar el contenido para preservar info útil.

- [ ] **Step 2: Sobrescribir README.md raíz con contenido VYNTIA**

Reemplazar `README.md` raíz con:

```markdown
# VYNTIA

> SaaS modular de gestión de Recursos Humanos para Perú.
> *Donde el talento se convierte en valor.*

## Estructura del monorepo

```
vyntia/
├── apps/
│   ├── api/          # Backend Django (Python 3.11+)
│   └── web/          # Frontend React + Vite (Node 20+)
├── packages/         # Librerías compartidas (vacío en L0)
├── docs/             # Documentación del producto y arquitectura
│   ├── 00_VYNTIA_MAESTRO.md
│   ├── arquitectura/
│   ├── modulos/
│   ├── normativa/
│   ├── comercial/
│   └── superpowers/  # Specs y plans del workflow de desarrollo
├── scripts/          # Scripts admin one-off
└── .github/          # CI/CD workflows
```

## Setup local

### Backend
```bash
cd apps/api
python -m venv ../../.venv
source ../../.venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
python manage.py migrate --settings=config.settings.development
python manage.py runserver --settings=config.settings.development
```

### Frontend
```bash
cd apps/web
npm install
npm run dev
```

O desde la raíz: `npm run dev:web`.

## Estado del proyecto

VYNTIA está en migración desde el proyecto INTRANET previo. Ver
`docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md`
para el plan completo.

**Capa actual:** L0 — Bootstrap del monorepo.

## Licencia

TBD por el dueño del proyecto.
```

- [ ] **Step 3: Verificar archivo creado**

Run:
```bash
head -20 README.md
```

Expected: muestra "# VYNTIA" como primera línea.

- [ ] **Step 4: Commit**

Run:
```bash
git add README.md
git commit -m "chore(L0): replace README with VYNTIA placeholder"
```

---

## Task 10: Smoke tests finales

**Files:** ninguno (solo verificación end-to-end)

- [ ] **Step 1: Verificar estructura final**

Run:
```bash
ls -la
```

Expected: incluye `apps/`, `packages/`, `docs/`, `scripts/`, `.github/`, `package.json`, `README.md`, `.gitignore`. NO debe incluir `back/`, `front/`, `saas_rrhh/`.

- [ ] **Step 2: Backend smoke test completo**

Run:
```bash
cd apps/api
python manage.py check --settings=config.settings.development
pytest -x --tb=short 2>&1 | tail -10
```

Expected:
- `check`: `System check identified no issues`
- `pytest`: mismo número de tests verdes que el baseline en Task 2 Step 1.

Si hay regresiones, **detente** y diagnostica. La promesa de L0 es "cero cambios funcionales".

- [ ] **Step 3: Backend runserver smoke**

Run:
```bash
python manage.py runserver --settings=config.settings.development 2>&1 &
SERVER_PID=$!
sleep 5
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/api/docs/ || echo "curl failed"
kill $SERVER_PID 2>/dev/null
```

Expected: `200` o `301`/`302` (cualquier código != 000 indica que el servidor responde). Si es `000` o curl falla, el server no arrancó.

- [ ] **Step 4: Frontend smoke test completo**

Run:
```bash
cd ../web
npm run build 2>&1 | tail -10
npm test -- --run --reporter=basic 2>&1 | tail -10
```

Expected:
- `build`: `✓ built in Xs`
- `test`: mismo resultado que baseline.

- [ ] **Step 5: Verificar git history**

Run:
```bash
cd ../..
git log --oneline vyntia/L0-bootstrap ^master | head -20
```

Expected: 7+ commits con prefijo `chore(L0):` (uno por cada task que commiteó).

- [ ] **Step 6: Verificar que el árbol está limpio**

Run:
```bash
git status --short
```

Expected: salida vacía. Cualquier archivo residual indica trabajo incompleto.

---

## Task 11: Merge a master (o crear PR)

**Files:** ninguno

- [ ] **Step 1: Confirmar con el usuario antes de mergear**

Pregunta al usuario:
- ¿Quieres mergear a master ahora, o crear PR para review?
- Si es repo solo y local, `git checkout master && git merge vyntia/L0-bootstrap --no-ff` está bien.
- Si hay remote y proceso de PR, push: `git push origin vyntia/L0-bootstrap` y crear PR.

**NO mergear sin autorización del usuario.**

- [ ] **Step 2: Si autoriza merge directo:**

Run:
```bash
git checkout master
git merge vyntia/L0-bootstrap --no-ff -m "Merge L0: monorepo bootstrap"
git log --oneline -5
```

Expected: merge commit visible en log. Branch `vyntia/L0-bootstrap` puede borrarse (`git branch -d vyntia/L0-bootstrap`) pero NO sin autorización.

- [ ] **Step 3: Verificar último smoke test post-merge**

Run:
```bash
cd apps/api && pytest -x --tb=short 2>&1 | tail -5
cd ../web && npm run build 2>&1 | tail -5
cd ../..
```

Expected: ambos verdes.

---

## Definition of Done — checklist final

Marcar cada item solo cuando esté verificado:

- [ ] `ls` muestra `apps/`, `packages/`, `docs/`, `scripts/`, `.github/`, `package.json`, `README.md`
- [ ] `ls` NO muestra `back/`, `front/`, `saas_rrhh/`
- [ ] `cd apps/api && pytest` pasa con mismo número de tests que el baseline
- [ ] `cd apps/api && python manage.py runserver` arranca sin errores
- [ ] `cd apps/web && npm run build` construye exitosamente
- [ ] `cd apps/web && npm test` pasa con mismo resultado que baseline
- [ ] `npm run dev:web` desde raíz arranca el frontend
- [ ] `docs/00_VYNTIA_MAESTRO.md` existe (renombrado del original)
- [ ] `docs/arquitectura/`, `docs/modulos/`, `docs/normativa/`, `docs/comercial/` existen
- [ ] `package.json` raíz declara workspaces
- [ ] `.gitignore` raíz cubre Python, Node, IDEs, secrets
- [ ] `README.md` dice VYNTIA en lugar de INTRANET
- [ ] Branch `vyntia/L0-bootstrap` tiene 7+ commits con prefijo `chore(L0):`
- [ ] `git status` está limpio
- [ ] (Opcional) Branch mergeada a master con autorización del usuario

---

## Después de L0

**Próximo plan:** L1 — Rebrand superficial (BD `bd_vyntia`, settings module rename, design tokens, Inter font, logo VYNTIA).

Cuando termines L0:
1. Confirmar con el usuario que las apps se ven y funcionan exactamente como antes (mismas páginas, mismos endpoints, mismos datos).
2. Solicitar generar el plan de L1 invocando nuevamente la skill `superpowers:writing-plans` con el siguiente sub-spec.

---

## Notas para el ejecutor

- **Cada task es atómica y commiteable.** Si algo sale mal en task N, el revert es `git reset --hard HEAD~1` y se conserva todo lo de tasks 1..N-1.
- **NO toques código Python o TypeScript en L0.** Si encuentras un import absoluto roto al hacer un move, eso significa que hay algo no obvio — anota y consulta. No "arregles" con un patch en L0.
- **Si pytest baseline tenía fallos pre-L0 documentados como aceptados**, está bien que sigan fallando igual después. La regla es "no introducir nuevos fallos", no "arreglar fallos preexistentes".
- **Windows Git Bash**: usar `source .venv/Scripts/activate` (no `.venv/bin/activate`). Forward slashes funcionan en paths.
- **Si npm install se queja de versions de Node**, el `engines` en package.json es advisory; ajustar `engines` o instalar Node 20+.
