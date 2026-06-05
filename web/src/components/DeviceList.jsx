export function DeviceList({ device }) {
  return (
    <section className="card">
      <h2>Current device</h2>
      {device ? (
        <ul className="plain-list">
          <li><strong>Name:</strong> {device.deviceName}</li>
          <li><strong>ID:</strong> {device.deviceId}</li>
          <li><strong>Public key:</strong> {device.publicKey}</li>
        </ul>
      ) : <p>No device registered yet.</p>}
    </section>
  );
}
