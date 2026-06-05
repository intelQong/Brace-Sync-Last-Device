const DEFAULT_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8787';

async function request(path, options = {}) {
  const response = await fetch(`${DEFAULT_API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'content-type': 'application/json',
      ...(options.headers ?? {})
    }
  });
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.error?.message || `API request failed: ${response.status}`);
  }
  return body;
}

export const api = {
  createSession: () => request('/sync/new'),
  registerDevice: (sessionId, device) => request(`/sync/${sessionId}/register`, {
    method: 'POST',
    body: JSON.stringify(device)
  }),
  getSession: (sessionId) => request(`/sync/${sessionId}/session`),
  deleteSession: (sessionId) => request(`/sync/${sessionId}/session`, { method: 'DELETE' }),
  uploadData: (sessionId, dataType, payload) => request(`/sync/${sessionId}/data/${dataType}`, {
    method: 'PUT',
    body: JSON.stringify(payload)
  }),
  downloadData: (sessionId, dataType) => request(`/sync/${sessionId}/data/${dataType}`),
  listData: (sessionId) => request(`/sync/${sessionId}/data`),
  createBackup: (sessionId, payload) => request(`/sync/${sessionId}/backup`, {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  listBackups: (sessionId) => request(`/sync/${sessionId}/backup`)
};
