import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Configure before the modules read process.env; never call external APIs in tests.
process.env.ALLOWED_SENDERS = 'me@example.com';
process.env.SUMMARY_PROVIDER = 'local';

const { extractText } = await import('../src/extract.js');
const { parseCommand, runCommand } = await import('../src/commands.js');
const { buildReply, isTrustedSender, extractAddress } = await import('../src/gmail.js');

const fixtures = path.join(path.dirname(fileURLToPath(import.meta.url)), 'fixtures');
const read = (name) => fs.readFileSync(path.join(fixtures, name));

test('extracts text from every supported fixture', async () => {
  assert.match(await extractText('a.pdf', read('sample.pdf')), /Invoice 42: total due 300 USD/);
  assert.match(await extractText('a.docx', read('sample.docx')), /Revenue grew 15% in Q3/);
  assert.match(await extractText('a.html', read('sample.html')), /Revenue grew 15% in Q3/);
  assert.match(await extractText('a.txt', read('sample.txt')), /Quarterly report/);
  const xlsx = await extractText('a.xlsx', read('sample.xlsx'));
  assert.match(xlsx, /## Budget/);
  assert.match(xlsx, /Servers\t1200/);
  assert.match(xlsx, /Total\t1200/);
  await assert.rejects(extractText('a.exe', Buffer.from('x')), /не поддерживается/);
});

test('parses commands from the subject only when it starts with one', () => {
  assert.deepEqual(parseCommand('convert PDF'), { name: 'CONVERT', args: ['PDF'] });
  assert.deepEqual(parseCommand('ORGANIZE Отчёты 2026'), { name: 'ORGANIZE', args: ['Отчёты', '2026'] });
  assert.deepEqual(parseCommand('EXTRACT: documents'), { name: 'EXTRACT', args: ['documents'] });
  assert.equal(parseCommand('Re: EXTRACT documents'), null);
  assert.equal(parseCommand('Привет, как дела?'), null);
  assert.equal(parseCommand(''), null);
});

test('trusts only allowed senders that are self-sent or pass DMARC', () => {
  const base = { fromAddress: 'me@example.com', labelIds: ['INBOX'], authResults: '' };
  assert.equal(isTrustedSender({ ...base, labelIds: ['INBOX', 'SENT'] }), true);
  assert.equal(isTrustedSender({ ...base, authResults: 'mx.google.com; spf=pass; dmarc=pass (p=NONE)' }), true);
  assert.equal(isTrustedSender({ ...base, authResults: 'mx.google.com; dmarc=fail' }), false);
  assert.equal(isTrustedSender(base), false);
  assert.equal(isTrustedSender({ ...base, fromAddress: 'evil@example.com', labelIds: ['SENT'] }), false);
  assert.equal(extractAddress('Me <Me@Example.com>'), 'me@example.com');
});

test('builds a threaded MIME reply with marker header and attachment', () => {
  const original = {
    from: 'Me <me@example.com>',
    subject: 'SUMMARY отчёт',
    messageIdHeader: '<abc@mail.gmail.com>',
    references: '',
  };
  const mime = buildReply(original, {
    text: 'Готово',
    attachments: [{ filename: 'out.txt', mimeType: 'text/plain', content: Buffer.from('hello') }],
  });
  assert.match(mime, /^To: Me <me@example\.com>\r\n/);
  assert.match(mime, /Subject: =\?UTF-8\?B\?/);
  assert.match(mime, /In-Reply-To: <abc@mail\.gmail\.com>/);
  assert.match(mime, /X-AI-Assistant: reply/);
  assert.match(mime, /filename="out\.txt"/);
  assert.ok(mime.includes(Buffer.from('Готово').toString('base64')));
});

test('EXTRACT and SUMMARY commands produce replies from attachments', async () => {
  const files = [
    { filename: 'report.docx', mimeType: 'application/octet-stream', content: read('sample.docx') },
    { filename: 'invoice.pdf', mimeType: 'application/pdf', content: read('sample.pdf') },
  ];
  const extracted = await runCommand(parseCommand('EXTRACT'), { files });
  assert.match(extracted.text, /report\.docx/);
  assert.match(extracted.text, /Invoice 42/);
  assert.deepEqual(extracted.attachments.map((a) => a.filename), ['report.txt', 'invoice.txt']);

  const summary = await runCommand(parseCommand('SUMMARY'), { files });
  assert.match(summary.text, /\[local\]/);
  assert.match(summary.text, /Revenue grew 15%/);

  const empty = await runCommand(parseCommand('SUMMARY'), { files: [] });
  assert.match(empty.text, /нет вложений/);

  const noTarget = await runCommand(parseCommand('CONVERT'), { files });
  assert.match(noTarget.text, /Укажите формат/);
});
