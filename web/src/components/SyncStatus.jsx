export function SyncStatus({ state }) {
  return (
    <section className="card">
      <h2>Sync status</h2>
      <dl className="grid">
        <div><dt>Session</dt><dd>{state.sessionId || 'Not created'}</dd></div>
        <div><dt>Last sync</dt><dd>{state.lastSyncAt || 'Never'}</dd></div>
        <div><dt>Bookmarks</dt><dd>{state.bookmarks.length}</dd></div>
        <div><dt>Auto sync</dt><dd>{state.autoSync ? 'Enabled' : 'Disabled'}</dd></div>
      </dl>
    </section>
  );
}
