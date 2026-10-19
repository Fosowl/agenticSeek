import fs from 'node:fs/promises';
import { google } from 'googleapis';
import { authenticate } from '@google-cloud/local-auth';
import { config, SCOPES } from './config.js';

async function loadSavedClient() {
  try {
    const saved = JSON.parse(await fs.readFile(config.tokenPath, 'utf8'));
    return google.auth.fromJSON(saved);
  } catch {
    return null;
  }
}

async function saveClient(client) {
  const keys = JSON.parse(await fs.readFile(config.credentialsPath, 'utf8'));
  const key = keys.installed || keys.web;
  const payload = {
    type: 'authorized_user',
    client_id: key.client_id,
    client_secret: key.client_secret,
    refresh_token: client.credentials.refresh_token,
  };
  await fs.writeFile(config.tokenPath, JSON.stringify(payload, null, 2), { mode: 0o600 });
}

/**
 * Returns an authorized OAuth2 client. Opens the browser for consent on first run
 * (or when `interactive` is forced) and stores the refresh token in token.json.
 */
export async function getAuthClient({ interactive = false } = {}) {
  if (!interactive) {
    const saved = await loadSavedClient();
    if (saved) return saved;
  }

  try {
    await fs.access(config.credentialsPath);
  } catch {
    throw new Error(
      `Не найден ${config.credentialsPath}. Скачайте OAuth Client ID (Desktop app) из Google Cloud Console — см. README.md.`,
    );
  }

  const client = await authenticate({ scopes: SCOPES, keyfilePath: config.credentialsPath });
  if (!client.credentials.refresh_token) {
    throw new Error(
      'Google не вернул refresh_token. Отзовите доступ приложения на https://myaccount.google.com/permissions и запустите `npm run auth` снова.',
    );
  }
  await saveClient(client);
  return client;
}
