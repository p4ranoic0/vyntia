---
phase: 01-onboarding-self-service
plan: "11"
subsystem: frontend-onboarding
tags: [react, modal, file-preview, document-upload, ux]
dependency_graph:
  requires: ["01-09"]
  provides: ["DocumentPreviewModal", "preview-before-upload flow"]
  affects: ["DocumentUploadZone"]
tech_stack:
  added: []
  patterns: ["blob URL lifecycle", "useEffect cleanup for URL.revokeObjectURL", "Dialog modal pattern"]
key_files:
  created:
    - front/src/features/onboarding/components/DocumentPreviewModal.tsx
  modified:
    - front/src/features/onboarding/components/DocumentUploadZone.tsx
decisions:
  - "DocumentPreviewModal uses useEffect cleanup to revoke blob URL on modal close — prevents memory leaks"
  - "onDropAccepted intercepts file selection and sets pendingFile+isPreviewOpen instead of calling handleUpload directly"
  - "DocumentPreviewModal placed before the dropzone div in a React Fragment so it renders as a portal overlay"
  - "Existing onDropRejected logic unchanged — file-too-large and format errors still fire toast.error() immediately without modal"
metrics:
  duration: "8 min"
  completed_date: "2026-03-15"
  tasks_completed: 2
  files_changed: 2
---

# Phase 1 Plan 11: Document Preview Modal — Summary

## One-liner

Preview-before-upload flow: file drop opens DocumentPreviewModal with blob URL iframe/img preview; upload only fires on "Enviar documento" confirm.

## What Was Built

### Task 1: DocumentPreviewModal component (new file)

Created `front/src/features/onboarding/components/DocumentPreviewModal.tsx` with:

- Props: `file`, `archivoUrl`, `label`, `isOpen`, `isUploading`, `onConfirm`, `onCancel`
- Creates a blob URL via `URL.createObjectURL(file)` inside a `useEffect` that runs when `isOpen` is true
- Blob URL is released via `URL.revokeObjectURL(url)` in the useEffect cleanup function — called when modal closes or file changes
- Renders `<iframe>` for PDFs and `<img>` for images (detected via `file.type.startsWith('image/')` or URL regex)
- Displays file size in MB in the dialog title
- Buttons: "Cancelar" (calls `onCancel`, disabled during upload) and "Enviar documento" (calls `onConfirm`, shows "Enviando..." during upload)
- Uses shadcn/ui Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter

### Task 2: DocumentUploadZone modified (preview intercept)

Modified `front/src/features/onboarding/components/DocumentUploadZone.tsx` with:

- Added import: `import { DocumentPreviewModal } from './DocumentPreviewModal'`
- Added two state variables: `pendingFile: File | null` and `isPreviewOpen: boolean`
- Changed `onDropAccepted` from calling `handleUpload(files[0])` directly to setting `setPendingFile(files[0])` and `setIsPreviewOpen(true)`
- Added `handlePreviewConfirm`: calls `handleUpload(pendingFile)`, closes modal, clears pendingFile
- Added `handlePreviewCancel`: closes modal, clears pendingFile (discards file)
- Wrapped dropzone return in a React Fragment `<>` with `<DocumentPreviewModal>` rendered before the dropzone div
- `onDropRejected` logic unchanged — size/format errors still fire `toast.error()` immediately

## Deviations from Plan

None — plan executed exactly as written.

## Success Criteria Verification

- [x] DocumentPreviewModal.tsx exports DocumentPreviewModal with correct props interface
- [x] Modal shows iframe for PDFs, img for images, using URL.createObjectURL for pre-upload files
- [x] Modal has "Cancelar" and "Enviar documento" buttons
- [x] Blob URL is revoked on modal close via useEffect cleanup
- [x] DocumentUploadZone onDropAccepted no longer calls handleUpload directly — sets pendingFile and opens modal
- [x] handlePreviewConfirm triggers the actual upload
- [x] handlePreviewCancel discards the file and closes modal
- [x] Existing toast.error() for size/format errors still fires immediately (unchanged)
- [x] TypeScript: no errors in modified/created onboarding files (pre-existing example file errors are out of scope)

## Self-Check

### Files Created/Modified

- `front/src/features/onboarding/components/DocumentPreviewModal.tsx` — FOUND
- `front/src/features/onboarding/components/DocumentUploadZone.tsx` — FOUND (modified)

## Self-Check: PASSED
