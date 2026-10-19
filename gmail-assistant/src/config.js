import path from 'node:path';
import { fileURLToPath } from 'node:url';
import dotenv from 'dotenv';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
dotenv.config({ path: path.join(ROOT, '.env'), quiet: true });

function list(value) {
  return (value || '')
    .split(',')
    .map((s) => s.trim().toLowerCase())
    .filter(Boolean);
}

export const config = {
  credentialsPath: path.resolve(ROOT, process.env.GOOGLE_CREDENTIALS_PATH || 'credentials.json'),
  tokenPath: path.resolve(ROOT, process.env.GOOGLE_TOKEN_PATH || 'token.json'),

  // Only emails from these addresses are treated as commands. Required.
  allowedSenders: list(process.env.ALLOWED_SENDERS),

  pollIntervalMs: Number(process.env.POLL_INTERVAL_MS || 60_000),
  processedLabel: process.env.PROCESSED_LABEL || 'AI-Assistant/Processed',
  driveRootFolder: process.env.DRIVE_ROOT_FOLDER || 'AI Assistant',

  // Limits that protect against huge attachments and oversized replies.
  maxAttachmentBytes: Number(process.env.MAX_ATTACHMENT_MB || 20) * 1024 * 1024,
  maxReplyTextChars: Number(process.env.MAX_REPLY_TEXT_CHARS || 20_000),

  claudeModel: process.env.CLAUDE_MODEL || 'claude-opus-5-5',
  // Set SUMMARY_PROVIDER=local to never call the Claude API.
  summaryProvider: (process.env.SUMMARY_PROVIDER || 'claude').toLowerCase(),
};

// Read-modify Gmail (read, label, reply) and Drive access limited to files this app creates.
export const SCOPES = [
  'https://www.googleapis.com/auth/gmail.modify',
  'https://www.googleapis.com/auth/drive.file',
];
