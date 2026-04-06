---
phase: 1
slug: onboarding-self-service
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-django (back), Vitest (front) |
| **Config file** | `back/pytest.ini` / `back/Makefile` (`make test`), `front/vite.config.ts` |
| **Quick run command** | `cd D:/INTRANET/back && D:/INTRANET/.venv/Scripts/python.exe -m pytest tests/test_onboarding*.py -x -v` |
| **Full suite command** | `cd D:/INTRANET/back && make test` / `cd D:/INTRANET/front && npm run test` |
| **Estimated runtime** | ~30 seconds (backend quick), ~90 seconds (full suite) |

---

## Sampling Rate

- **After every task commit:** Run `cd D:/INTRANET/back && D:/INTRANET/.venv/Scripts/python.exe -m pytest tests/test_onboarding*.py -x`
- **After every plan wave:** Run `cd D:/INTRANET/back && make test && cd D:/INTRANET/front && npm run test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 0 | ONBD-01 | unit | `pytest tests/test_onboarding_service.py -x` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 0 | ONBD-01 | unit | `pytest tests/test_onboarding_api.py::test_corregir_correo -x` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 0 | ONBD-03 | unit | `pytest tests/test_onboarding_api.py::test_photo_upload -x` | ❌ W0 | ⬜ pending |
| 1-01-04 | 01 | 0 | ONBD-04 | unit | `pytest tests/test_onboarding_service.py::test_actualizar_estado_dni -x` | ❌ W0 | ⬜ pending |
| 1-01-05 | 01 | 0 | ONBD-05 | unit | `pytest tests/test_onboarding_service.py::test_actualizar_estado_familiar -x` | ❌ W0 | ⬜ pending |
| 1-01-06 | 01 | 0 | ONBD-06 | unit | `pytest tests/test_onboarding_service.py::test_actualizar_estado_academico -x` | ❌ W0 | ⬜ pending |
| 1-01-07 | 01 | 0 | ONBD-07 | unit | `pytest tests/test_onboarding_service.py::test_actualizar_estado_laboral -x` | ❌ W0 | ⬜ pending |
| 1-01-08 | 01 | 0 | ONBD-08 | unit | `pytest tests/test_onboarding_api.py::test_list_includes_progreso -x` | ❌ W0 | ⬜ pending |
| 1-02-01 | 02 | 1 | ONBD-02 | manual | N/A — browser routing guard test | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `back/tests/test_onboarding_service.py` — stubs for ONBD-01, ONBD-04, ONBD-05, ONBD-06, ONBD-07 service-level assertions
- [ ] `back/tests/test_onboarding_api.py` — stubs for ONBD-01 (corregir-correo), ONBD-03 (photo upload), ONBD-08 (list response fields)
- [ ] `back/tests/conftest.py` — verify `onboarding_factory` fixture exists; add if absent

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Employee with active onboarding cannot access /admin routes or other employees' data | ONBD-02 | Routing guard is browser-side React navigation; unit tests can't fully cover the redirect behavior in context | Log in as onboarding employee → navigate to /admin → verify redirect to onboarding view |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
