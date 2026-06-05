const STORAGE_KEY = 'privacy-sync-state-v1';

const defaultState = {
  user: null,
  device: null,
  sessionId: '',
  bookmarks: [],
  encryptedBackup: null,
  lastSyncAt: null,
  autoSync: false,
  syncIntervalMinutes: 30
};

export function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? { ...defaultState, ...JSON.parse(raw) } : { ...defaultState };
  } catch {
    return { ...defaultState };
  }
}

export function saveState(nextState) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(nextState));
  return nextState;
}

export function clearState() {
  localStorage.removeItem(STORAGE_KEY);
}

export function exportStateSnapshot(state) {
  return {
    sessionId: state.sessionId,
    device: state.device,
    bookmarks: state.bookmarks,
    exportedAt: new Date().toISOString()
  };
}
