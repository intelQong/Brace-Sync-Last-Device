import { encryptJson } from '@privacy-sync/shared';
import { api } from '../services/api.js';
import { exportStateSnapshot } from '../services/storage.js';

export function useSync(state, setState) {
  async function createSession() {
    const result = await api.createSession();
    setState((current) => ({ ...current, sessionId: result.sessionId }));
    return result.sessionId;
  }

  async function registerDevice() {
    const sessionId = state.sessionId || await createSession();
    if (!state.device) throw new Error('Sign in and create a device first');
    await api.registerDevice(sessionId, state.device);
    setState((current) => ({ ...current, sessionId, lastSyncAt: new Date().toISOString() }));
  }

  async function syncNow(password) {
    const sessionId = state.sessionId || await createSession();
    if (!state.device) throw new Error('Sign in and create a device first');
    await api.registerDevice(sessionId, state.device);
    const encryptedData = await encryptJson(
      { bookmarks: state.bookmarks },
      password,
      { sessionId, dataType: 'bookmarks' }
    );
    await api.uploadData(sessionId, 'bookmarks', { deviceId: state.device.deviceId, dataType: 'bookmarks', encryptedData });
    setState((current) => ({ ...current, sessionId, lastSyncAt: new Date().toISOString() }));
  }

  async function createRecoveryBackup(password) {
    const sessionId = state.sessionId || await createSession();
    if (!state.device) throw new Error('Sign in and create a device first');
    const encryptedBackup = await encryptJson(exportStateSnapshot({ ...state, sessionId }), password, {
      sessionId,
      type: 'recovery-backup'
    });
    const result = await api.createBackup(sessionId, {
      deviceId: state.device.deviceId,
      deviceName: state.device.deviceName,
      encryptedBackup
    });
    setState((current) => ({ ...current, sessionId, encryptedBackup: result.backup, lastSyncAt: new Date().toISOString() }));
  }

  return { createSession, registerDevice, syncNow, createRecoveryBackup };
}
