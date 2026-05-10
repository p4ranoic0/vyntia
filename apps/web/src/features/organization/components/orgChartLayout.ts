import dagre from 'dagre'
import type { Edge, Node } from '@xyflow/react'

/** Layout dimensions used by dagre for hierarchical org-chart placement. */
const NODE_WIDTHS = {
  department: 240,
  position: 200,
  employee: 190,
} as const

const NODE_HEIGHTS = {
  department: 90,
  position: 70,
  employee: 56,
} as const

/**
 * Compute hierarchical (top-down) positions for the given nodes/edges using
 * dagre. Returns a new node array with `position: {x, y}` set; edges unchanged.
 *
 * The layout uses TB (top-to-bottom) direction with generous spacing for
 * orgchart readability.
 */
export function applyDagreLayout(
  nodes: Node[],
  edges: Edge[],
): { nodes: Node[]; edges: Edge[] } {
  const g = new dagre.graphlib.Graph()
  g.setGraph({ rankdir: 'TB', nodesep: 60, ranksep: 80, marginx: 20, marginy: 20 })
  g.setDefaultEdgeLabel(() => ({}))

  nodes.forEach((node) => {
    const w = NODE_WIDTHS[node.type as keyof typeof NODE_WIDTHS] ?? 200
    const h = NODE_HEIGHTS[node.type as keyof typeof NODE_HEIGHTS] ?? 70
    g.setNode(node.id, { width: w, height: h })
  })

  edges.forEach((edge) => {
    g.setEdge(edge.source, edge.target)
  })

  dagre.layout(g)

  const positionedNodes = nodes.map((node) => {
    const layouted = g.node(node.id)
    if (!layouted) return node
    return {
      ...node,
      position: {
        x: layouted.x - (g.node(node.id)?.width ?? 200) / 2,
        y: layouted.y - (g.node(node.id)?.height ?? 70) / 2,
      },
    }
  })

  return { nodes: positionedNodes, edges }
}
