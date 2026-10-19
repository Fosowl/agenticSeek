import { setTimeout as sleep } from 'node:timers/promises';
import { config } from './config.js';
import { getAuthClient } from './auth.js';
import { driveClient } from './drive.js';
import {
  addLabel,
  downloadAttachment,
  ensureLabel,
  gmailClient,
  isTrustedSender,
  listCandidateMessages,
  sendReply,
} from './gmail.js';
import { parseCommand, runCommand } from './commands.js';

const MAX_REPLY_ATTACHMENTS_BYTES = 20 * 1024 * 1024; // Gmail rejects messages over ~25 MB

function log(...args) {
  console.log(new Date().toISOString(), ...args);
}

async function loadFiles(gmail, msg) {
  const files = [];
  const skipped = [];
  for (const a of msg.attachments) {
    if (a.size > config.maxAttachmentBytes) {
      skipped.push(`${a.filename} (${(a.size / 1048576).toFixed(1)} МБ — больше лимита)`);
      continue;
    }
    files.push({ filename: a.filename, mimeType: a.mimeType, content: await downloadAttachment(gmail, msg.id, a.attachmentId) });
  }
  return { files, skipped };
}

function fitAttachments(reply) {
  const attachments = [];
  const dropped = [];
  let total = 0;
  for (const a of reply.attachments || []) {
    if (total + a.content.length > MAX_REPLY_ATTACHMENTS_BYTES) {
      dropped.push(a.filename);
      continue;
    }
    total += a.content.length;
    attachments.push(a);
  }
  const note = dropped.length ? `\n\nНе поместились в письмо (лимит Gmail): ${dropped.join(', ')}` : '';
  return { text: reply.text + note, attachments };
}

async function processMessage({ gmail, drive, msg, labelId }) {
  if (msg.isOwnReply) return;
  const command = parseCommand(msg.subject);
  if (!command) return; // ordinary email — leave it untouched

  if (!isTrustedSender(msg)) {
    log(`[skip] «${msg.subject}» от ${msg.fromAddress}: отправитель не прошёл проверку (DMARC/SENT)`);
    await addLabel(gmail, msg.id, labelId);
    return;
  }

  log(`[cmd] ${command.name} ${command.args.join(' ')} — «${msg.subject}», вложений: ${msg.attachments.length}`);
  let reply;
  try {
    const { files, skipped } = await loadFiles(gmail, msg);
    reply = await runCommand(command, { gmail, drive, msg, files });
    if (skipped.length) reply.text += `\n\nПропущены: ${skipped.join(', ')}`;
  } catch (err) {
    log(`[error] ${command.name}:`, err);
    reply = { text: `Не удалось выполнить ${command.name}: ${err.message}` };
  }

  await sendReply(gmail, msg, fitAttachments(reply));
  // Label only after replying, so a crash mid-way means the command is retried, not lost.
  await addLabel(gmail, msg.id, labelId);
  log(`[done] ${command.name} — ответ отправлен`);
}

async function poll(ctx) {
  const messages = await listCandidateMessages(ctx.gmail, ctx.labelId);
  for (const msg of messages) {
    try {
      await processMessage({ ...ctx, msg });
    } catch (err) {
      log(`[error] сообщение ${msg.id}:`, err.message);
    }
  }
}

async function main() {
  const argv = new Set(process.argv.slice(2));

  if (argv.has('--auth')) {
    await getAuthClient({ interactive: true });
    log(`Авторизация выполнена, токен сохранён в ${config.tokenPath}`);
    return;
  }

  if (!config.allowedSenders.length) {
    throw new Error('ALLOWED_SENDERS не задан в .env — укажите адреса, которым разрешено отправлять команды.');
  }

  const auth = await getAuthClient();
  const gmail = gmailClient(auth);
  const drive = driveClient(auth);
  const labelId = await ensureLabel(gmail, config.processedLabel);
  const ctx = { gmail, drive, labelId };

  log(`Ассистент запущен. Разрешённые отправители: ${config.allowedSenders.join(', ')}`);

  if (argv.has('--once')) {
    await poll(ctx);
    return;
  }

  const stop = new AbortController();
  for (const sig of ['SIGINT', 'SIGTERM']) {
    process.on(sig, () => {
      log('Остановка…');
      stop.abort();
    });
  }

  while (!stop.signal.aborted) {
    try {
      await poll(ctx);
    } catch (err) {
      log('[error] опрос Gmail:', err.message);
    }
    await sleep(config.pollIntervalMs, null, { signal: stop.signal }).catch(() => {});
  }
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
