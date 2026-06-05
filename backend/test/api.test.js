import assert from 'node:assert/strict';
import { test } from 'node:test';
import { handleRequest, InMemorySessionStore } from '../src/index.js';

async function api(store, path, init = {}) {
  const response = await handleRequest(new Request(`https://api.test${path}`, init), { store });
  const body = await response.json();
  return { response, body };
}

test('session lifecycle, device registration, encrypted data, and backups', async () => {
  const store = new InMemorySessionStore();
  const created = await api(store, '/sync/new');
  assert.equal(created.response.status, 201);
  const { sessionId } = created.body;

  const registered = await api(store, `/sync/${sessionId}/register`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ deviceId: 'd1', deviceName: 'iPhone', publicKey: 'pub' })
  });
  assert.equal(registered.body.session.devices.length, 1);

  const stored = await api(store, `/sync/${sessionId}/data/bookmarks`, {
    method: 'PUT',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ deviceId: 'd1', encryptedData: { ciphertext: 'abc', nonce: 'n' } })
  });
  assert.equal(stored.body.status, 'stored');

  const downloaded = await api(store, `/sync/${sessionId}/data/bookmarks`);
  assert.equal(downloaded.body.data.encryptedData.ciphertext, 'abc');

  const backup = await api(store, `/sync/${sessionId}/backup`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ deviceId: 'd1', deviceName: 'iPhone', encryptedBackup: { ciphertext: 'backup' } })
  });
  assert.equal(backup.response.status, 201);

  const listed = await api(store, `/sync/${sessionId}/backup`);
  assert.equal(listed.body.backups.length, 1);
});

test('unknown session returns 404', async () => {
  const store = new InMemorySessionStore();
  const result = await api(store, '/sync/missing/session');
  assert.equal(result.response.status, 404);
});
