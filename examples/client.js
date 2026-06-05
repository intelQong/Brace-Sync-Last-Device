const API = 'https://privacy-sync.example.workers.dev';

async function createSession() {
  const response = await fetch(`${API}/sync/new`);
  return response.json();
}

async function registerDevice(sessionId) {
  const response = await fetch(`${API}/sync/${sessionId}/register`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ deviceId: 'device_1', deviceName: 'iPhone', publicKey: 'public-key' })
  });
  return response.json();
}

async function uploadEncryptedBookmarks(sessionId, encryptedData) {
  const response = await fetch(`${API}/sync/${sessionId}/data/bookmarks`, {
    method: 'PUT',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ deviceId: 'device_1', dataType: 'bookmarks', encryptedData })
  });
  return response.json();
}

export { createSession, registerDevice, uploadEncryptedBookmarks };
