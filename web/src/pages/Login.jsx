import { useState } from 'react';

export function Login({ onSignIn }) {
  const [email, setEmail] = useState('');
  const [deviceName, setDeviceName] = useState('');

  function submit(event) {
    event.preventDefault();
    onSignIn(email, deviceName);
  }

  return (
    <main className="center-panel">
      <section className="card hero">
        <p className="eyebrow">End-to-end encrypted browser sync</p>
        <h1>Protect your last synced device</h1>
        <p>Start with a free web app that stores encrypted bookmarks and recovery backups through a Cloudflare backend.</p>
        <form onSubmit={submit} className="form">
          <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
          <label>Device name<input value={deviceName} onChange={(event) => setDeviceName(event.target.value)} placeholder="iPhone, Android, Desktop" /></label>
          <button type="submit">Continue</button>
        </form>
      </section>
    </main>
  );
}
