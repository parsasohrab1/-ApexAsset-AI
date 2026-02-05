import { authService } from './auth'

const API_BASE =
  (import.meta.env.VITE_API_URL as string | undefined) ??
  'http://localhost:8000'

interface FetchOptions extends RequestInit {
  requiresAuth?: boolean
}

export async function apiFetch(
  endpoint: string,
  options: FetchOptions = {}
): Promise<Response> {
  const { requiresAuth = true, ...fetchOptions } = options

  const headers = new Headers(fetchOptions.headers)

  if (requiresAuth) {
    const token = authService.getAccessToken()
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
  }

  let response = await fetch(`${API_BASE}${endpoint}`, {
    ...fetchOptions,
    headers,
  })

  // If unauthorized and we have a refresh token, try to refresh
  if (response.status === 401 && requiresAuth) {
    try {
      const newToken = await authService.refreshAccessToken()
      headers.set('Authorization', `Bearer ${newToken}`)

      // Retry the original request
      response = await fetch(`${API_BASE}${endpoint}`, {
        ...fetchOptions,
        headers,
      })
    } catch (error) {
      // Refresh failed, redirect to login
      authService.logout()
      window.location.href = '/login'
      throw error
    }
  }

  return response
}
