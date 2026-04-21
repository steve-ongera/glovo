const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

async function request(method, endpoint, data = null, options = {}) {
  const token = localStorage.getItem('access_token')
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const config = { method, headers }
  if (data) config.body = JSON.stringify(data)

  let res = await fetch(`${BASE_URL}${endpoint}`, config)

  if (res.status === 401 && token) {
    const refresh = localStorage.getItem('refresh_token')
    if (refresh) {
      const rr = await fetch(`${BASE_URL}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      })
      if (rr.ok) {
        const rd = await rr.json()
        localStorage.setItem('access_token', rd.access)
        headers['Authorization'] = `Bearer ${rd.access}`
        res = await fetch(`${BASE_URL}${endpoint}`, { ...config, headers })
      } else {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }
  }

  const json = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = new Error(JSON.stringify(json))
    err.data = json
    err.status = res.status
    throw err
  }
  return { data: json, status: res.status }
}

const api = {
  get: (ep, opts) => request('GET', ep, null, opts),
  post: (ep, data, opts) => request('POST', ep, data, opts),
  put: (ep, data, opts) => request('PUT', ep, data, opts),
  patch: (ep, data, opts) => request('PATCH', ep, data, opts),
  delete: (ep, opts) => request('DELETE', ep, null, opts),
}

export default api

export const formatPrice = (amount) =>
  `Ksh ${Number(amount).toLocaleString('en-KE', { minimumFractionDigits: 0 })}`

export const getErrorMessage = (err) => {
  try {
    const data = JSON.parse(err.message)
    const msgs = Object.values(data).flat()
    return msgs[0] || 'Something went wrong'
  } catch {
    return err.message || 'Something went wrong'
  }
}