const JSON_HEADERS = {
  'content-type': 'application/json; charset=utf-8',
  'cache-control': 'no-store'
};

const CORS_HEADERS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
  'access-control-allow-headers': 'content-type,authorization'
};

function nowIso() {
  return new Date().toISOString();
}

function randomId(prefix) {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  const suffix = btoa(String.fromCharCode(...bytes)).replaceAll('+', '-').replaceAll('/', '_').replaceAll('=', '');
  return `${prefix}${suffix}`;
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { ...JSON_HEADERS, ...CORS_HEADERS }
  });
}

function error(message, status = 400, details = undefined) {
  return json({ error: { message, details } }, status);
}

async function readJson(request) {
  if (!request.body) return {};
  try {
    return await request.json();
  } catch {
    throw new Error('Request body must be valid JSON');
  }
}

function assertString(value, name) {
  if (typeof value !== 'string' || !value.trim()) {
    throw new Error(`${name} is required`);
  }
  return value.trim();
}

function publicSession(session) {
  return {
    sessionId: session.sessionId,
    createdAt: session.createdAt,
    updatedAt: session.updatedAt,
    devices: Object.values(session.devices),
    dataTypes: Object.values(session.data).map((record) => ({
      dataType: record.dataType,
      uploadedAt: record.uploadedAt,
      uploadedBy: record.uploadedBy,
      version: record.version
    })),
    backups: Object.values(session.backups).map((backup) => ({
      backupId: backup.backupId,
      deviceId: backup.deviceId,
      deviceName: backup.deviceName,
      createdAt: backup.createdAt,
      updatedAt: backup.updatedAt,
      lastAccessedAt: backup.lastAccessedAt
    }))
  };
}

function newSession(sessionId) {
  const createdAt = nowIso();
  return {
    sessionId,
    createdAt,
    updatedAt: createdAt,
    devices: {},
    data: {},
    backups: {}
  };
}

class DurableSessionStore {
  constructor(state) {
    this.state = state;
  }

  async get(sessionId) {
    return (await this.state.storage.get(`session:${sessionId}`)) ?? null;
  }

  async put(session) {
    session.updatedAt = nowIso();
    await this.state.storage.put(`session:${session.sessionId}`, session);
    return session;
  }

  async delete(sessionId) {
    await this.state.storage.delete(`session:${sessionId}`);
  }
}

export class InMemorySessionStore {
  constructor() {
    this.sessions = new Map();
  }

  async get(sessionId) {
    return this.sessions.get(sessionId) ?? null;
  }

  async put(session) {
    session.updatedAt = nowIso();
    this.sessions.set(session.sessionId, structuredClone(session));
    return session;
  }

  async delete(sessionId) {
    this.sessions.delete(sessionId);
  }
}

async function requireSession(store, sessionId) {
  const session = await store.get(sessionId);
  if (!session) throw Object.assign(new Error('Session not found'), { status: 404 });
  return session;
}

async function handleWithStore(request, store, url) {
  const method = request.method;
  const parts = url.pathname.split('/').filter(Boolean);

  if (method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS_HEADERS });
  if (parts[0] !== 'sync') return error('Not found', 404);

  if (method === 'GET' && parts.length === 2 && parts[1] === 'new') {
    const sessionId = randomId('session_');
    const session = await store.put(newSession(sessionId));
    return json({ status: 201, sessionId, endpoint: `/sync/${sessionId}`, session: publicSession(session) }, 201);
  }

  const sessionId = parts[1];
  if (!sessionId) return error('sessionId is required', 400);

  try {
    if (method === 'POST' && parts[2] === 'register') {
      const body = await readJson(request);
      const deviceId = assertString(body.deviceId ?? randomId('device_'), 'deviceId');
      const deviceName = assertString(body.deviceName, 'deviceName');
      const publicKey = assertString(body.publicKey, 'publicKey');
      const session = await requireSession(store, sessionId);
      session.devices[deviceId] = {
        deviceId,
        deviceName,
        publicKey,
        registeredAt: session.devices[deviceId]?.registeredAt ?? nowIso(),
        lastSeen: nowIso()
      };
      await store.put(session);
      return json({ status: 'ok', session: publicSession(session) });
    }

    if (method === 'GET' && parts[2] === 'session') {
      return json({ session: publicSession(await requireSession(store, sessionId)) });
    }

    if (method === 'DELETE' && parts[2] === 'session') {
      await store.delete(sessionId);
      return json({ status: 'deleted', sessionId });
    }

    if (parts[2] === 'data') {
      const session = await requireSession(store, sessionId);
      const dataType = parts[3];

      if (method === 'GET' && !dataType) {
        return json({ data: publicSession(session).dataTypes });
      }
      if (!dataType) return error('data type is required', 400);

      if (method === 'PUT') {
        const body = await readJson(request);
        const deviceId = assertString(body.deviceId, 'deviceId');
        const encryptedData = body.encryptedData;
        if (!encryptedData || typeof encryptedData !== 'object') throw new Error('encryptedData object is required');
        session.data[dataType] = {
          dataType,
          encryptedData,
          uploadedAt: nowIso(),
          uploadedBy: deviceId,
          version: (session.data[dataType]?.version ?? 0) + 1
        };
        await store.put(session);
        return json({ status: 'stored', data: publicSession(session).dataTypes.find((item) => item.dataType === dataType) });
      }

      if (method === 'GET') {
        const record = session.data[dataType];
        if (!record) return error('Encrypted data not found', 404);
        return json({ data: record });
      }

      if (method === 'DELETE') {
        delete session.data[dataType];
        await store.put(session);
        return json({ status: 'deleted', dataType });
      }
    }

    if (parts[2] === 'backup') {
      const session = await requireSession(store, sessionId);
      const backupId = parts[3];

      if (method === 'POST' && !backupId) {
        const body = await readJson(request);
        const id = randomId('backup_');
        const deviceId = assertString(body.deviceId, 'deviceId');
        const deviceName = assertString(body.deviceName, 'deviceName');
        if (!body.encryptedBackup || typeof body.encryptedBackup !== 'object') throw new Error('encryptedBackup object is required');
        const timestamp = nowIso();
        session.backups[id] = {
          backupId: id,
          deviceId,
          deviceName,
          encryptedBackup: body.encryptedBackup,
          createdAt: timestamp,
          updatedAt: timestamp,
          lastAccessedAt: null
        };
        await store.put(session);
        return json({ status: 'created', backup: publicSession(session).backups.find((item) => item.backupId === id) }, 201);
      }

      if (method === 'GET' && !backupId) {
        return json({ backups: publicSession(session).backups });
      }
      if (!backupId) return error('backupId is required', 400);
      const backup = session.backups[backupId];
      if (!backup) return error('Backup not found', 404);

      if (method === 'GET') {
        backup.lastAccessedAt = nowIso();
        await store.put(session);
        return json({ backup });
      }

      if (method === 'PUT') {
        const body = await readJson(request);
        backup.deviceName = body.deviceName ? String(body.deviceName) : backup.deviceName;
        backup.updatedAt = nowIso();
        await store.put(session);
        return json({ status: 'updated', backup: publicSession(session).backups.find((item) => item.backupId === backupId) });
      }

      if (method === 'DELETE') {
        delete session.backups[backupId];
        await store.put(session);
        return json({ status: 'deleted', backupId });
      }
    }
  } catch (caught) {
    return error(caught.message, caught.status ?? 400);
  }

  return error('Not found', 404);
}

async function dispatchToDurableObject(request, env) {
  const id = env.SYNC_SESSIONS.idFromName('global-session-store');
  const stub = env.SYNC_SESSIONS.get(id);
  return stub.fetch(request);
}

export async function handleRequest(request, env = {}) {
  const url = new URL(request.url);
  if (env.store) return handleWithStore(request, env.store, url);
  if (env.SYNC_SESSIONS) return dispatchToDurableObject(request, env);
  return error('Storage binding is not configured', 500);
}

export class SyncSessionDurableObject {
  constructor(state, env) {
    this.state = state;
    this.env = env;
    this.store = new DurableSessionStore(state);
  }

  async fetch(request) {
    return handleWithStore(request, this.store, new URL(request.url));
  }
}

export default {
  fetch: handleRequest
};
