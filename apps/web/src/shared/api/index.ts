/**
 * Shared API infrastructure barrel.
 *
 * Re-exports the canonical axios client, React Query setup, normalizers,
 * and error utilities. Consumers may import from `@/shared/api` for
 * convenience or from the explicit submodule path.
 */
export { apiClient } from "./api";
export type {
  ApiResponse,
  AuthResponse,
  Permission,
  Role,
  User,
} from "./api";
export { queryClient } from "./queryClient";
export {
  getErrorMessage,
  isAuthError,
  isAuthorizationError,
  isServerError,
  isValidationError,
} from "./errorUtils";
export {
  extractCollection,
  normalizeEmployee,
  normalizeRole,
  normalizeSecurityRole,
  normalizeUser,
} from "./apiNormalizers";
