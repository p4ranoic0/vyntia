---
phase: 0
slug: infrastructure-fixes
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
---

# Phase 0 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (backend) |
| **Config file** | `back/pytest.ini` or `back/Makefile` |
| **Quick run command** | `cd back && D:/INTRANET/.venv/Scripts/python.exe -m pytest tests/ -x -q --settings=config.settings.testing` |
| **Full suite command** | `cd back && make test` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick pytest on affected test file
- **After every plan wave:** Run full suite (`make test`)
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 0-01-01 | 01 | 1 | INFRA-01 | manual | `python -c "import config.settings.production"` | ✅ | ⬜ pending |
| 0-01-02 | 01 | 1 | INFRA-02 | unit | `pytest tests/test_settings.py -v` | ❌ W0 | ⬜ pending |
| 0-01-03 | 01 | 1 | INFRA-03 | unit | `pytest tests/test_pdf_generator.py -v` | ❌ W0 | ⬜ pending |
| 0-01-04 | 01 | 1 | INFRA-04 | unit | `pytest tests/test_documentos_digitales.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `back/tests/test_settings.py` — verify PostgreSQL ENGINE in development.py, psycopg2-binary present in requirements.txt, mysqlclient absent
- [ ] `back/tests/test_pdf_generator.py` — verify generated PDF bytes contain real content (not "DOCUMENTO GENERADO"), verify fallback chain skips WeasyPrint on Windows
- [ ] `back/tests/test_documentos_digitales.py` — verify `tamano_archivo_legible` does not mutate `self.tamano_archivo`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Django starts without SyntaxError in production | INFRA-01 | Syntax errors prevent import — can't test with pytest | Run `python -c "import config.settings.production"` and verify no SyntaxError |
| PDF renders HTML template content | INFRA-03 | Requires real Django template rendering + file output | Generate a test certificate via the API, open the PDF and confirm it contains real text |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
