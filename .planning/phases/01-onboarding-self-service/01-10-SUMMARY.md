---
plan: "01-10"
phase: "01-onboarding-self-service"
status: complete
date: "2026-03-15"
---

# Plan 01-10 Summary: Frontend Accordion Tabs — N-Item Dynamic Forms

## What Was Built

1. **`accordion.tsx`** — Accordion, AccordionItem, AccordionTrigger, AccordionContent UI components (shadcn/ui pattern)

2. **`onboardingDataService.ts`** — 12 exported async functions:
   - `getFamiliares`, `createFamiliar`, `updateFamiliar`, `deleteFamiliar`
   - `getAcademicos`, `createAcademico`, `updateAcademico`
   - `getCursos`, `createCurso`, `updateCurso`, `deleteCurso`
   - `getConstanciasTrabajo`

3. **`onboarding.ts` types extended** — added `acta_matrimonio`, `certificado_capacitacion`, `constancia_trabajo` to `TipoDocumento`

4. **`OnboardingTabFamiliar.tsx` rewritten** — N-item familiar form with "Agregar dependiente" dialog, per-parentesco `DocumentUploadZone` instances wired to `onboardingDataService`

5. **`OnboardingTabAcademico.tsx` rewritten** — 3 Accordion sections (certificados/cursos/titulos) each with "Agregar" dialogs and upload zones

6. **`OnboardingTabLaboral.tsx` rewritten** — keeps read-only RRHH section + static upload zones + new "Experiencia Laboral" accordion section

## Commits

- `c62a48a9`: feat(01-10): add accordion UI, onboardingDataService with CRUD calls, extend TipoDocumento
- `33b09c20`: feat(01-10): rewrite Familiar/Academico/Laboral tabs with N-item accordion forms and upload zones

## Key Files

### Created
- `front/src/components/ui/accordion.tsx`
- `front/src/features/onboarding/services/onboardingDataService.ts`

### Modified
- `front/src/features/onboarding/types/onboarding.ts`
- `front/src/features/onboarding/components/OnboardingTabFamiliar.tsx`
- `front/src/features/onboarding/components/OnboardingTabAcademico.tsx`
- `front/src/features/onboarding/components/OnboardingTabLaboral.tsx`

## Verification

- TypeScript: no errors in onboarding feature files
- All 6 files found on disk after write

## Self-Check: PASSED
