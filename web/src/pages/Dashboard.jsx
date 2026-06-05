import { useState } from 'react';
import { DeviceList } from '../components/DeviceList.jsx';
import { SyncStatus } from '../components/SyncStatus.jsx';

export function Dashboard({ state, sync }) {
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  async function run(action) {
    setMessage('Working...');
    try {
      await action();
      setMessage('Done');
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <main className="page-grid">
      <SyncStatus state={state} />
      <DeviceList device={state.device} />
      <section className="card wide">
        <h2>Manual sync</h2>
        <p>Enter a recovery password. It is used locally to encrypt the bookmarks payload before upload.</p>
        <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Recovery password" />
        <div className="actions">
          <button onClick={() => run(sync.createSession)}>Create session</button>
          <button onClick={() => run(sync.registerDevice)}>Register device</button>
          <button onClick={() => run(() => sync.syncNow(password))} disabled={!password}>Sync bookmarks</button>
          <button onClick={() => run(() => sync.createRecoveryBackup(password))} disabled={!password}>Create backup</button>
        </div>
        {message && <p className="notice">{message}</p>}
      </section>
    </main>
  );
}
