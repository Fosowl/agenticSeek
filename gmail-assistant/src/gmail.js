import { google } from 'googleapis';
import { config } from './config.js';

export function gmailClient(auth) {
  return google.gmail({ version: 'v1', auth });
}

export async function ensureLabel(gmail, name) {
  const { data } = await gmail.users.labels.list({ userId: 'me' });
  const existing = (data.labels || []).find((l) => l.name === name);
  if (existing) return existing.id;
  const created = await gmail.users.labels.create({
    userId: 'me',
    requestBody: { name, labelListVisibility: 'labelShow', messageListVisibility: 'show' },
  });
  return created.data.id;
}

/** Recent inbox messages from allowed senders that were not processed yet. */
export async function listCandidateMessages(gmail, processedLabelId) {
  const from = config.allowedSenders.map((a) => `from:${a}`).join(' OR ');
  // Gmail search spells "/" in label names as "-".
  const labelQuery = config.processedLabel.replace(/[/\s]/g, '-');
  const q = `in:inbox newer_than:3d -label:${labelQuery} {${from}}`;

  const ids = [];
  let pageToken;
  do {
    const { data } = await gmail.users.messages.list({ userId: 'me', q, maxResults: 50, pageToken });
    ids.push(...(data.messages || []).map((m) => m.id));
    pageToken = data.nextPageToken;
  } while (pageToken && ids.length < 200);

  const messages = [];
  for (const id of ids) {
    const { data } = await gmail.users.messages.get({ userId: 'me', id, format: 'full' });
    if (!(data.labelIds || []).includes(processedLabelId)) messages.push(parseMessage(data));
  }
  // Oldest first, so commands run in the order they were sent.
  return messages.sort((a, b) => Number(a.internalDate) - Number(b.internalDate));
}

function header(headers, name) {
  const h = headers.find((x) => x.name.toLowerCase() === name.toLowerCase());
  return h ? h.value : '';
}

export function extractAddress(fromHeader) {
  const m = fromHeader.match(/<([^>]+)>/);
  return (m ? m[1] : fromHeader).trim().toLowerCase();
}

function decodeBody(data) {
  return Buffer.from(data, 'base64url').toString('utf8');
}

function walkParts(part, out) {
  if (!part) return;
  if (part.filename && part.body?.attachmentId) {
    out.attachments.push({
      filename: part.filename,
      mimeType: part.mimeType,
      size: part.body.size,
      attachmentId: part.body.attachmentId,
    });
  } else if (part.mimeType === 'text/plain' && part.body?.data && !out.text) {
    out.text = decodeBody(part.body.data);
  }
  for (const p of part.parts || []) walkParts(p, out);
}

export function parseMessage(data) {
  const headers = data.payload?.headers || [];
  const out = { text: '', attachments: [] };
  walkParts(data.payload, out);
  return {
    id: data.id,
    threadId: data.threadId,
    internalDate: data.internalDate,
    labelIds: data.labelIds || [],
    from: header(headers, 'From'),
    fromAddress: extractAddress(header(headers, 'From')),
    to: header(headers, 'To'),
    subject: header(headers, 'Subject'),
    messageIdHeader: header(headers, 'Message-ID'),
    references: header(headers, 'References'),
    authResults: header(headers, 'Authentication-Results'),
    isOwnReply: header(headers, 'X-AI-Assistant') !== '',
    text: out.text,
    attachments: out.attachments,
  };
}

/**
 * The From header alone is trivial to forge. Accept a message only if it came from
 * an allowed address AND either was sent from this very account (Gmail adds the
 * SENT label) or passed DMARC according to Gmail's own Authentication-Results.
 */
export function isTrustedSender(msg) {
  if (!config.allowedSenders.includes(msg.fromAddress)) return false;
  if (msg.labelIds.includes('SENT')) return true;
  return /\bdmarc=pass\b/i.test(msg.authResults);
}

export async function downloadAttachment(gmail, messageId, attachmentId) {
  const { data } = await gmail.users.messages.attachments.get({
    userId: 'me',
    messageId,
    id: attachmentId,
  });
  return Buffer.from(data.data, 'base64url');
}

export async function addLabel(gmail, messageId, labelId) {
  await gmail.users.messages.modify({
    userId: 'me',
    id: messageId,
    requestBody: { addLabelIds: [labelId], removeLabelIds: ['UNREAD'] },
  });
}

function encodeHeader(value) {
  // RFC 2047 for non-ASCII subjects (e.g. Cyrillic).
  return /^[\x20-\x7e]*$/.test(value) ? value : `=?UTF-8?B?${Buffer.from(value).toString('base64')}?=`;
}

function chunk64(buf) {
  return buf.toString('base64').replace(/.{76}/g, '$&\r\n');
}

/** Builds a multipart MIME reply in the original thread. */
export function buildReply(original, { text, attachments = [] }) {
  const boundary = `b_${Date.now().toString(36)}_${Math.random().toString(36).slice(2)}`;
  const subject = /^re:/i.test(original.subject) ? original.subject : `Re: ${original.subject}`;
  const refs = [original.references, original.messageIdHeader].filter(Boolean).join(' ');

  const lines = [
    `To: ${original.from}`,
    `Subject: ${encodeHeader(subject)}`,
    original.messageIdHeader ? `In-Reply-To: ${original.messageIdHeader}` : null,
    refs ? `References: ${refs}` : null,
    // Marks our own replies so the poller never treats them as new commands.
    'X-AI-Assistant: reply',
    'MIME-Version: 1.0',
    `Content-Type: multipart/mixed; boundary="${boundary}"`,
    '',
    `--${boundary}`,
    'Content-Type: text/plain; charset="UTF-8"',
    'Content-Transfer-Encoding: base64',
    '',
    chunk64(Buffer.from(text, 'utf8')),
  ].filter((l) => l !== null);

  for (const a of attachments) {
    const name = encodeHeader(a.filename);
    lines.push(
      `--${boundary}`,
      `Content-Type: ${a.mimeType}; name="${name}"`,
      `Content-Disposition: attachment; filename="${name}"`,
      'Content-Transfer-Encoding: base64',
      '',
      chunk64(a.content),
    );
  }
  lines.push(`--${boundary}--`, '');
  return lines.join('\r\n');
}

export async function sendReply(gmail, original, reply) {
  const raw = Buffer.from(buildReply(original, reply)).toString('base64url');
  await gmail.users.messages.send({
    userId: 'me',
    requestBody: { raw, threadId: original.threadId },
  });
}
