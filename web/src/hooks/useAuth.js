import { randomId } from '@privacy-sync/shared';

export function useAuth(state, setState) {
  function signIn(email, deviceName) {
    const user = { email, signedInAt: new Date().toISOString() };
    const device = state.device ?? {
      deviceId: randomId('device_'),
      deviceName: deviceName || 'Web device',
      publicKey: randomId('public_')
    };
    setState((current) => ({ ...current, user, device }));
  }

  function signOut() {
    setState((current) => ({ ...current, user: null }));
  }

  return { user: state.user, device: state.device, signIn, signOut };
}
