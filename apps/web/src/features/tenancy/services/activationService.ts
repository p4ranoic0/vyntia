import { apiClient } from '@/shared/api/api'

export interface ActivationRequest {
  token: string
  name: string
  password: string
}

export interface ActivationResponse {
  access: string
  refresh: string
  tenant: { slug: string; name: string }
  user: { id: string; email: string; username: string }
  role: string
}

export async function activateInvitation(
  payload: ActivationRequest,
): Promise<ActivationResponse> {
  const response = await apiClient.post('/api/v1/auth/activate/', payload)
  return response.data?.data
}
