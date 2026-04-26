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
