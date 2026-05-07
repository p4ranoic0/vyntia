// Exportaciones de páginas de usuarios
export { default as UsersList } from './UsersList'
export { default as UsersForm } from './UsersForm'
export { default as UsersManagement } from './UsersManagement'
export { default as ChangePassword } from './ChangePassword'
export { default as RoleManagement } from './RoleManagement'
export { default as AdminDashboard } from './AdminDashboard'

// Tipos relacionados con usuarios
export type {
  User,
  Role,
  Permission,
  UserFormData,
  ChangePasswordData,
  UserRoleAssignment
} from '@/features/identity/services/usersService'