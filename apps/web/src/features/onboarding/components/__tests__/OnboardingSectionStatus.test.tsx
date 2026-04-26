import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { computeStatus, OnboardingSectionStatus } from '../OnboardingSectionStatus'
import type { DocumentInfo } from '../../types/onboarding'

const makeDoc = (tipo: string, estado: string): DocumentInfo => ({
  documento_id: Math.floor(Math.random() * 100000),
  tipo_documento: tipo as DocumentInfo['tipo_documento'],
  nombre_documento: tipo,
  estado_documento: estado as DocumentInfo['estado_documento'],
  fecha_subida: null,
})

describe('computeStatus', () => {
  it('returns pendiente when no docs provided', () => {
    expect(computeStatus([], ['dni', 'foto'])).toBe('pendiente')
  })

  it('returns pendiente when docs exist but none match section tipos', () => {
    const docs = [makeDoc('cv', 'aprobado')]
    expect(computeStatus(docs, ['dni', 'foto'])).toBe('pendiente')
  })

  it('returns observado when any matching doc is rechazado', () => {
    const docs = [makeDoc('dni', 'aprobado'), makeDoc('foto', 'rechazado')]
    expect(computeStatus(docs, ['dni', 'foto'])).toBe('observado')
  })

  it('returns completo when all section docs are aprobado', () => {
    const docs = [makeDoc('dni', 'aprobado'), makeDoc('foto', 'aprobado')]
    expect(computeStatus(docs, ['dni', 'foto'])).toBe('completo')
  })

  it('returns en_revision when some are pendiente_revision and none rechazado', () => {
    const docs = [makeDoc('dni', 'aprobado'), makeDoc('foto', 'pendiente_revision')]
    expect(computeStatus(docs, ['dni', 'foto'])).toBe('en_revision')
  })
})

describe('OnboardingSectionStatus', () => {
  it('renders 4 section labels', () => {
    render(<OnboardingSectionStatus docs={[]} />)
    expect(screen.getByText('Personal')).toBeDefined()
    expect(screen.getByText('Familiar')).toBeDefined()
    expect(screen.getByText(/cadémico/i)).toBeDefined()
    expect(screen.getByText('Laboral')).toBeDefined()
  })
})
