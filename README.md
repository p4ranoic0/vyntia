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

VYNTIA está en migración desde un repo intranet legacy. Ver
`docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md`
para el plan completo.

**Capa actual:** L1 — Rebrand superficial. Próximo: L2 — Django 5 upgrade.

## Licencia

TBD por el dueño del proyecto.
