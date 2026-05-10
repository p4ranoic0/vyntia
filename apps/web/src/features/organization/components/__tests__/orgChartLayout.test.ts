import { describe, expect, it } from 'vitest'
import type { Edge, Node } from '@xyflow/react'
import { applyDagreLayout } from '../orgChartLayout'

describe('applyDagreLayout', () => {
  it('assigns positions to all input nodes', () => {
    const nodes: Node[] = [
      { id: 'd1', type: 'department', data: {}, position: { x: 0, y: 0 } },
      { id: 'd2', type: 'department', data: {}, position: { x: 0, y: 0 } },
      { id: 'p1', type: 'position', data: {}, position: { x: 0, y: 0 } },
    ]
    const edges: Edge[] = [
      { id: 'e1', source: 'd1', target: 'd2' },
      { id: 'e2', source: 'd2', target: 'p1' },
    ]

    const result = applyDagreLayout(nodes, edges)
    expect(result.nodes).toHaveLength(3)
    result.nodes.forEach((n) => {
      expect(n.position.x).toBeTypeOf('number')
      expect(n.position.y).toBeTypeOf('number')
    })
  })

  it('lays out child below parent (top-down direction)', () => {
    const nodes: Node[] = [
      { id: 'parent', type: 'department', data: {}, position: { x: 0, y: 0 } },
      { id: 'child', type: 'department', data: {}, position: { x: 0, y: 0 } },
    ]
    const edges: Edge[] = [{ id: 'e', source: 'parent', target: 'child' }]

    const result = applyDagreLayout(nodes, edges)
    const parent = result.nodes.find((n) => n.id === 'parent')!
    const child = result.nodes.find((n) => n.id === 'child')!
    // Child should be vertically below parent in TB layout
    expect(child.position.y).toBeGreaterThan(parent.position.y)
  })

  it('returns edges unchanged', () => {
    const nodes: Node[] = [
      { id: 'a', type: 'department', data: {}, position: { x: 0, y: 0 } },
      { id: 'b', type: 'department', data: {}, position: { x: 0, y: 0 } },
    ]
    const edges: Edge[] = [{ id: 'e', source: 'a', target: 'b' }]

    const result = applyDagreLayout(nodes, edges)
    expect(result.edges).toEqual(edges)
  })

  it('handles empty input gracefully', () => {
    const result = applyDagreLayout([], [])
    expect(result.nodes).toEqual([])
    expect(result.edges).toEqual([])
  })

  it('uses different sizes per node type', () => {
    const nodes: Node[] = [
      { id: 'dept', type: 'department', data: {}, position: { x: 0, y: 0 } },
      { id: 'pos', type: 'position', data: {}, position: { x: 0, y: 0 } },
      { id: 'emp', type: 'employee', data: {}, position: { x: 0, y: 0 } },
    ]
    const edges: Edge[] = [
      { id: 'e1', source: 'dept', target: 'pos' },
      { id: 'e2', source: 'pos', target: 'emp' },
    ]
    // Smoke: layout succeeds without throwing for mixed node types
    const result = applyDagreLayout(nodes, edges)
    expect(result.nodes).toHaveLength(3)
  })
})
