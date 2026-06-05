export function Settings({ state, setState, auth }) {
  return (
    <main className="page-grid">
      <section className="card">
        <h1>Settings</h1>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={state.autoSync}
            onChange={(event) => setState((current) => ({ ...current, autoSync: event.target.checked }))}
          />
          Enable auto sync reminder
        </label>
        <label>
          Sync interval minutes
          <input
            type="number"
            min="5"
            value={state.syncIntervalMinutes}
            onChange={(event) => setState((current) => ({ ...current, syncIntervalMinutes: Number(event.target.value) }))}
          />
        </label>
        <button className="danger" onClick={auth.signOut}>Logout</button>
      </section>
      <section className="card">
        <h2>Backup info</h2>
        <p>Latest backup: {state.encryptedBackup?.backupId || 'None'}</p>
        <p>The recovery password is never stored. Keep it somewhere safe.</p>
      </section>
    </main>
  );
}
