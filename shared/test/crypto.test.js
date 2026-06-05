import assert from 'node:assert/strict';
import { test } from 'node:test';
import { decryptJson, encryptJson, randomId } from '../src/crypto.js';

test('encryptJson/decryptJson round trips JSON without plaintext leakage', async () => {
  const aad = { sessionId: 'session-1', type: 'bookmarks' };
  const envelope = await encryptJson({ bookmarks: [{ title: 'Brave', url: 'https://brave.com' }] }, 'passphrase', aad);

  assert.equal(envelope.algorithm, 'AES-GCM');
  assert.notEqual(envelope.ciphertext.includes('Brave'), true);
  assert.deepEqual(await decryptJson(envelope, 'passphrase', aad), {
    bookmarks: [{ title: 'Brave', url: 'https://brave.com' }]
  });
});

test('decryptJson rejects wrong password and aad', async () => {
  const envelope = await encryptJson({ secret: true }, 'correct', { type: 'backup' });

  await assert.rejects(() => decryptJson(envelope, 'wrong', { type: 'backup' }));
  await assert.rejects(() => decryptJson(envelope, 'correct', { type: 'other' }));
});

test('randomId adds prefix and is URL safe', () => {
  assert.match(randomId('session_'), /^session_[A-Za-z0-9_-]+$/);
});
