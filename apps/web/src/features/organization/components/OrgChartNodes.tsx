import { memo } from 'react'
import { Handle, Position as HandlePosition, type NodeProps } from '@xyflow/react'
import { Building2, Briefcase, User } from 'lucide-react'

const UNIT_TYPE_BADGE: Record<string, string> = {
  direccion: 'bg-purple-100 text-purple-800',
  gerencia: 'bg-blue-100 text-blue-800',
  subgerencia: 'bg-cyan-100 text-cyan-800',
  oficina: 'bg-green-100 text-green-800',
  area: 'bg-amber-100 text-amber-800',
  equipo: 'bg-rose-100 text-rose-800',
}

export interface DepartmentNodeData {
  label: string
  siglas: string
  unit_type?: string
  empleados_count?: number
  [key: string]: unknown
}

export const DepartmentNode = memo(function DepartmentNode({
  data,
}: NodeProps) {
  const d = data as unknown as DepartmentNodeData
  const badge = UNIT_TYPE_BADGE[d.unit_type ?? 'area'] ?? 'bg-gray-100 text-gray-800'
  return (
    <div className="rounded-lg border-2 border-blue-300 bg-white shadow-md min-w-[220px] max-w-[280px] overflow-hidden">
      <Handle type="target" position={HandlePosition.Top} className="!bg-blue-400" />
      <div className="bg-blue-50 px-3 py-2 border-b border-blue-200 flex items-center gap-2">
        <Building2 className="h-4 w-4 text-blue-700" />
        <span className="text-xs font-bold text-blue-900 uppercase tracking-wide">
          {d.siglas}
        </span>
        {d.unit_type && (
          <span className={`ml-auto px-2 py-0.5 rounded text-[10px] font-medium ${badge}`}>
            {d.unit_type}
          </span>
        )}
      </div>
      <div className="px-3 py-2">
        <p className="text-sm font-medium text-gray-900 leading-tight">{d.label}</p>
        {typeof d.empleados_count === 'number' && (
          <p className="text-[11px] text-gray-500 mt-1">
            {d.empleados_count} empleado{d.empleados_count === 1 ? '' : 's'}
          </p>
        )}
      </div>
      <Handle type="source" position={HandlePosition.Bottom} className="!bg-blue-400" />
    </div>
  )
})

export interface PositionNodeData {
  label: string
  code: string
  is_current?: boolean
  is_active?: boolean
  occupational_category_name?: string
  [key: string]: unknown
}

export const PositionNode = memo(function PositionNode({
  data,
}: NodeProps) {
  const d = data as unknown as PositionNodeData
  return (
    <div
      className={`rounded-md border bg-white shadow-sm min-w-[180px] max-w-[240px] overflow-hidden ${
        d.is_active === false ? 'opacity-50' : ''
      }`}
    >
      <Handle type="target" position={HandlePosition.Top} className="!bg-green-400" />
      <div className="bg-green-50 px-2 py-1 border-b border-green-200 flex items-center gap-1.5">
        <Briefcase className="h-3 w-3 text-green-700" />
        <span className="text-[10px] font-mono font-semibold text-green-900">{d.code}</span>
      </div>
      <div className="px-2 py-1.5">
        <p className="text-xs font-medium text-gray-900 leading-tight">{d.label}</p>
        {d.occupational_category_name && (
          <p className="text-[10px] text-gray-500 mt-0.5">{d.occupational_category_name}</p>
        )}
      </div>
      <Handle type="source" position={HandlePosition.Bottom} className="!bg-green-400" />
    </div>
  )
})

export interface EmployeeNodeData {
  label: string
  plaza_code?: string
  plaza_status?: 'vacante' | 'ocupada' | 'congelada' | 'eliminada'
  [key: string]: unknown
}

const PLAZA_STATUS_BADGE: Record<string, string> = {
  vacante: 'bg-yellow-100 text-yellow-800',
  ocupada: 'bg-green-100 text-green-800',
  congelada: 'bg-blue-100 text-blue-800',
  eliminada: 'bg-gray-200 text-gray-600',
}

export const EmployeeNode = memo(function EmployeeNode({
  data,
}: NodeProps) {
  const d = data as unknown as EmployeeNodeData
  const statusBadge = d.plaza_status
    ? PLAZA_STATUS_BADGE[d.plaza_status]
    : 'bg-gray-100 text-gray-700'
  return (
    <div className="rounded-md border bg-white shadow-sm min-w-[160px] max-w-[220px] overflow-hidden">
      <Handle type="target" position={HandlePosition.Top} className="!bg-amber-400" />
      <div className="px-2 py-1.5 flex items-center gap-2">
        <div className="w-7 h-7 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
          <User className="h-3.5 w-3.5 text-amber-700" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium text-gray-900 leading-tight truncate">
            {d.label || 'Vacante'}
          </p>
          {d.plaza_code && (
            <p className="text-[10px] font-mono text-gray-500">{d.plaza_code}</p>
          )}
        </div>
        {d.plaza_status && (
          <span className={`px-1.5 py-0.5 rounded text-[9px] font-semibold uppercase ${statusBadge}`}>
            {d.plaza_status.slice(0, 3)}
          </span>
        )}
      </div>
    </div>
  )
})

export const orgChartNodeTypes = {
  department: DepartmentNode,
  position: PositionNode,
  employee: EmployeeNode,
}
