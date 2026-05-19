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
pip install -e ".[dev]"
python manage.py migrate --settings=vyntia.settings.development
python manage.py runserver --settings=vyntia.settings.development
```

### Frontend
```bash
cd apps/web
npm install
npm run dev
```

O desde la raíz: `npm run dev:web`.

## Estado del proyecto

VYNTIA está en migración modular desde un repo intranet legacy.
Roadmap de sub-proyectos: `docs/ROADMAP_SUBPROJECTS.md`.

**Sub-proyectos completos:**
- **A — Foundation** (rebrand + reestructura + Django 5 LTS) — tag `foundation-complete`.
- **C — Multi-tenancy + RLS** (Postgres Row-Level Security + tenant context) — tag `c-multitenancy-complete`.
- **B — Vyntia Core funcional** (17 fases: polish wave + Módulos 01-03 completos) — tag `b-vyntia-core-complete`.

**Próximo:** **D — Vyntia Pay** (planilla peruana real: PLAME, T-Registro, AFPnet, CTS, gratificaciones).

Specs y plans en `docs/superpowers/{specs,plans,summaries}/`.

## Licencia

TBD por el dueño del proyecto.
