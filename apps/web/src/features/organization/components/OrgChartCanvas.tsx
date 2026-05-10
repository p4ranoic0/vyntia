import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  applyNodeChanges,
  useReactFlow,
  type Edge,
  type Node,
  type NodeChange,
  type NodeMouseHandler,
  type ReactFlowProps,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import { useAuth } from '@/features/auth/hooks/useAuth'
import { Card } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { toast } from 'sonner'
import {
  orgchartService,
  type OrgDepartment,
  type Plaza,
  type Position,
} from '../services/orgchartService'
import { applyDagreLayout } from './orgChartLayout'
import { orgChartNodeTypes } from './OrgChartNodes'

/** Build raw nodes + edges from API data (no positions yet — dagre fills those). */
function buildGraph(
  departments: OrgDepartment[],
  positions: Position[],
  plazas: Plaza[],
): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = []
  const edges: Edge[] = []

  // Department nodes
  for (const d of departments) {
    nodes.push({
      id: `dept-${d.id}`,
      type: 'department',
      data: {
        label: d.nombre_completo ?? d.nombre_unidad_organica ?? d.nombre_organo,
        siglas: d.siglas_area,
        unit_type: d.unit_type,
      },
      position: { x: 0, y: 0 },
    })
    if (d.area_padre) {
      edges.push({
        id: `dept-edge-${d.id}`,
        source: `dept-${d.area_padre}`,
        target: `dept-${d.id}`,
        type: 'smoothstep',
      })
    }
  }

  // Position nodes — only current versions
  for (const p of positions) {
    if (!p.is_current) continue
    nodes.push({
      id: `pos-${p.id}`,
      type: 'position',
      data: {
        label: p.name,
        code: p.code,
        is_current: p.is_current,
        is_active: p.is_active,
        occupational_category_name: p.occupational_category_name,
      },
      position: { x: 0, y: 0 },
    })
    edges.push({
      id: `pos-edge-${p.id}`,
      source: `dept-${p.department}`,
      target: `pos-${p.id}`,
      type: 'smoothstep',
    })
  }

  // Plaza/Employee nodes — one per non-deleted plaza
  for (const pl of plazas) {
    if (pl.status === 'eliminada') continue
    nodes.push({
      id: `plaza-${pl.id}`,
      type: 'employee',
      data: {
        label: pl.current_employee_name ?? 'Vacante',
        plaza_code: pl.code,
        plaza_status: pl.status,
      },
      position: { x: 0, y: 0 },
    })
    edges.push({
      id: `plaza-edge-${pl.id}`,
      source: `pos-${pl.position}`,
      target: `plaza-${pl.id}`,
      type: 'smoothstep',
    })
  }

  return { nodes, edges }
}

interface CanvasState {
  loading: boolean
  error: string | null
  nodes: Node[]
  edges: Edge[]
}

function OrgChartCanvasInner() {
  const auth = useAuth()
  const isEditor = auth.isAdminOrRRHH?.() ?? false

  const [state, setState] = useState<CanvasState>({
    loading: true,
    error: null,
    nodes: [],
    edges: [],
  })
  const [search, setSearch] = useState('')
  const { fitView } = useReactFlow()

  // Initial data load
  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const [departments, positions, plazas] = await Promise.all([
          orgchartService.listDepartments(),
          orgchartService.listPositions({ is_current: true }),
          orgchartService.listPlazas(),
        ])
        if (cancelled) return
        const built = buildGraph(departments, positions, plazas)
        const laid = applyDagreLayout(built.nodes, built.edges)
        setState({
          loading: false,
          error: null,
          nodes: laid.nodes,
          edges: laid.edges,
        })
        // Defer fitView until react-flow commits the layout
        setTimeout(() => {
          try {
            fitView({ padding: 0.2, duration: 300 })
          } catch {
            // fitView fails silently if instance not ready — ignore
          }
        }, 100)
      } catch (e) {
        if (cancelled) return
        setState({
          loading: false,
          error: e instanceof Error ? e.message : 'Error loading orgchart',
          nodes: [],
          edges: [],
        })
      }
    })()
    return () => {
      cancelled = true
    }
  }, [fitView])

  // Apply standard react-flow node changes (selection, position when dragged)
  const onNodesChange = useCallback((changes: NodeChange[]) => {
    setState((s) => ({ ...s, nodes: applyNodeChanges(changes, s.nodes) }))
  }, [])

  // Drop handler — fires when a node is dragged onto another. Reparenting logic.
  const onNodeDragStop: NodeMouseHandler = useCallback(
    async (_event, draggedNode) => {
      if (!isEditor) return

      // Find the node currently positioned closest to the dragged node's center
      // and treat that as the drop target. Only Department→Department reparent
      // and Position→Department move are supported in B.6; Employee swap is
      // handled separately via dedicated UI in a follow-up.
      const draggedCenter = {
        x: draggedNode.position.x + 100,
        y: draggedNode.position.y + 40,
      }
      let dropTarget: Node | null = null
      let minDist = Infinity
      for (const n of state.nodes) {
        if (n.id === draggedNode.id) continue
        if (n.type !== 'department') continue
        const c = { x: n.position.x + 120, y: n.position.y + 45 }
        const d = Math.hypot(c.x - draggedCenter.x, c.y - draggedCenter.y)
        if (d < 200 && d < minDist) {
          minDist = d
          dropTarget = n
        }
      }
      if (!dropTarget) return

      const draggedKind = draggedNode.type
      const draggedId = String(draggedNode.id).replace(/^(dept|pos|plaza)-/, '')
      const targetDeptId = String(dropTarget.id).replace(/^dept-/, '')

      try {
        if (draggedKind === 'department') {
          await orgchartService.reparentDepartment(draggedId, targetDeptId)
          toast.success('Departamento reparentado')
        } else if (draggedKind === 'position') {
          await orgchartService.movePositionToDepartment(draggedId, targetDeptId)
          toast.success('Puesto reasignado al departamento')
        } else {
          return
        }
        // Reload graph after a successful reorganization
        const [departments, positions, plazas] = await Promise.all([
          orgchartService.listDepartments(),
          orgchartService.listPositions({ is_current: true }),
          orgchartService.listPlazas(),
        ])
        const built = buildGraph(departments, positions, plazas)
        const laid = applyDagreLayout(built.nodes, built.edges)
        setState((s) => ({ ...s, nodes: laid.nodes, edges: laid.edges }))
      } catch (e) {
        toast.error(e instanceof Error ? e.message : 'Error reorganizando')
      }
    },
    [isEditor, state.nodes],
  )

  // Search-filter: hide non-matching nodes (and their isolated edges)
  const filtered = useMemo(() => {
    if (!search.trim()) return state
    const q = search.toLowerCase()
    const visible = new Set(
      state.nodes
        .filter((n) => {
          const data = n.data as { label?: string; code?: string; siglas?: string }
          return (
            (data.label && data.label.toLowerCase().includes(q)) ||
            (data.code && data.code.toLowerCase().includes(q)) ||
            (data.siglas && data.siglas.toLowerCase().includes(q))
          )
        })
        .map((n) => n.id),
    )
    // Include direct ancestors so context is visible
    let added = true
    while (added) {
      added = false
      for (const edge of state.edges) {
        if (visible.has(edge.target) && !visible.has(edge.source)) {
          visible.add(edge.source)
          added = true
        }
      }
    }
    return {
      ...state,
      nodes: state.nodes.map((n) => ({ ...n, hidden: !visible.has(n.id) })),
      edges: state.edges.map((e) => ({
        ...e,
        hidden: !visible.has(e.source) || !visible.has(e.target),
      })),
    }
  }, [state, search])

  if (state.loading) {
    return (
      <Card className="m-4 p-6 text-center text-muted-foreground">
        Cargando organigrama…
      </Card>
    )
  }
  if (state.error) {
    return (
      <Card className="m-4 p-6 text-center text-destructive">
        Error: {state.error}
      </Card>
    )
  }
  if (state.nodes.length === 0) {
    return (
      <Card className="m-4 p-6 text-center text-muted-foreground">
        Sin departamentos, puestos o plazas registrados todavía. RRHH puede
        comenzar creando departamentos y puestos.
      </Card>
    )
  }

  const reactFlowProps: ReactFlowProps = {
    nodes: filtered.nodes,
    edges: filtered.edges,
    onNodesChange,
    nodeTypes: orgChartNodeTypes,
    nodesDraggable: isEditor,
    nodesConnectable: false,
    elementsSelectable: true,
    onNodeDragStop: isEditor ? onNodeDragStop : undefined,
    fitView: true,
    minZoom: 0.2,
    maxZoom: 2,
  }

  return (
    <div className="w-full h-full relative">
      <div className="absolute top-4 left-4 z-10 w-72">
        <Input
          placeholder="Buscar por nombre, código o siglas…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-white shadow-md"
        />
      </div>
      {!isEditor && (
        <div className="absolute top-4 right-4 z-10 bg-white rounded-md shadow-md px-3 py-2 text-xs text-muted-foreground">
          Modo solo lectura
        </div>
      )}
      <ReactFlow {...reactFlowProps}>
        <Background gap={20} size={1} />
        <Controls />
        <MiniMap nodeStrokeWidth={3} pannable zoomable />
      </ReactFlow>
    </div>
  )
}

/** Top-level component — wraps inner canvas in ReactFlowProvider so the
 * useReactFlow hook works for fitView calls. */
export default function OrgChartCanvas() {
  return (
    <ReactFlowProvider>
      <OrgChartCanvasInner />
    </ReactFlowProvider>
  )
}
