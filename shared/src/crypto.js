const ENCODER = new TextEncoder();
const DECODER = new TextDecoder();

export const ENVELOPE_VERSION = 1;
export const DEFAULT_PBKDF2_ITERATIONS = 100_000;
export const AES_GCM_IV_BYTES = 12;
export const SALT_BYTES = 16;

function subtleCrypto() {
  if (!globalThis.crypto?.subtle) {
    throw new Error('Web Crypto API is required for client-side encryption');
  }
  return globalThis.crypto.subtle;
}

export function bytesToBase64(bytes) {
  if (typeof Buffer !== 'undefined') {
    return Buffer.from(bytes).toString('base64');
  }
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

export function base64ToBytes(value) {
  if (typeof Buffer !== 'undefined') {
    return new Uint8Array(Buffer.from(value, 'base64'));
  }
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

export function randomBytes(length) {
  const bytes = new Uint8Array(length);
  globalThis.crypto.getRandomValues(bytes);
  return bytes;
}

export function randomId(prefix = '') {
  const id = bytesToBase64(randomBytes(16)).replaceAll('+', '-').replaceAll('/', '_').replaceAll('=', '');
  return `${prefix}${id}`;
}

async function importPassword(password) {
  return subtleCrypto().importKey('raw', ENCODER.encode(password), 'PBKDF2', false, ['deriveKey']);
}

export async function deriveAesKey(password, salt, iterations = DEFAULT_PBKDF2_ITERATIONS) {
  if (!password) throw new Error('A non-empty password is required');
  const baseKey = await importPassword(password);
  return subtleCrypto().deriveKey(
    { name: 'PBKDF2', salt, iterations, hash: 'SHA-256' },
    baseKey,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
}

export async function encryptJson(plaintextValue, password, aad = {}) {
  const salt = randomBytes(SALT_BYTES);
  const iv = randomBytes(AES_GCM_IV_BYTES);
  const key = await deriveAesKey(password, salt);
  const plaintext = ENCODER.encode(JSON.stringify(plaintextValue));
  const additionalData = ENCODER.encode(JSON.stringify(aad));
  const ciphertext = await subtleCrypto().encrypt({ name: 'AES-GCM', iv, additionalData }, key, plaintext);

  return {
    version: ENVELOPE_VERSION,
    algorithm: 'AES-GCM',
    kdf: 'PBKDF2-SHA256',
    iterations: DEFAULT_PBKDF2_ITERATIONS,
    salt: bytesToBase64(salt),
    iv: bytesToBase64(iv),
    aad,
    ciphertext: bytesToBase64(new Uint8Array(ciphertext))
  };
}

export async function decryptJson(envelope, password, expectedAad = undefined) {
  if (envelope.version !== ENVELOPE_VERSION) {
    throw new Error(`Unsupported envelope version: ${envelope.version}`);
  }
  if (envelope.algorithm !== 'AES-GCM') {
    throw new Error(`Unsupported algorithm: ${envelope.algorithm}`);
  }
  if (expectedAad && JSON.stringify(envelope.aad) !== JSON.stringify(expectedAad)) {
    throw new Error('Encrypted envelope associated data did not match');
  }

  const salt = base64ToBytes(envelope.salt);
  const iv = base64ToBytes(envelope.iv);
  const ciphertext = base64ToBytes(envelope.ciphertext);
  const key = await deriveAesKey(password, salt, envelope.iterations);
  const additionalData = ENCODER.encode(JSON.stringify(envelope.aad ?? {}));
  const plaintext = await subtleCrypto().decrypt({ name: 'AES-GCM', iv, additionalData }, key, ciphertext);
  return JSON.parse(DECODER.decode(plaintext));
}
