import path from 'node:path';
import { config } from './config.js';
import { canExtract, docxToHtml, extOf, extractText } from './extract.js';
import { convertViaDrive, driveCanConvert, ensureFolderPath, mimeFor, uploadFile } from './drive.js';
import { summarize } from './summarize.js';

const COMMANDS = ['EXTRACT', 'SUMMARY', 'ORGANIZE', 'CONVERT', 'HELP'];

export const HELP_TEXT = `Команды (первое слово темы письма):

EXTRACT          — извлечь текст из вложений (PDF, DOCX, XLSX, HTML, TXT, CSV, JSON, MD)
SUMMARY          — краткое резюме каждого вложения
ORGANIZE [папка] — сохранить вложения в Google Drive: «${config.driveRootFolder}/<папка или дата>/<тип>»
CONVERT <формат> — конвертировать вложения: pdf, docx, xlsx, pptx, txt, html, csv
HELP             — эта справка

Пример темы: «CONVERT pdf» с вложением report.docx.`;

/** "CONVERT pdf" -> { name: "CONVERT", args: ["pdf"] }; returns null for non-commands (incl. "Re: ..."). */
export function parseCommand(subject) {
  const words = (subject || '').trim().split(/\s+/);
  const name = (words[0] || '').toUpperCase().replace(/[:.!]$/, '');
  if (!COMMANDS.includes(name)) return null;
  return { name, args: words.slice(1) };
}

function baseName(filename) {
  return path.basename(filename, path.extname(filename));
}

function clip(text, max) {
  return text.length > max ? `${text.slice(0, max)}\n\n… [обрезано, полный текст во вложении]` : text;
}

function noFiles() {
  return { text: 'В письме нет вложений. Прикрепите документ и отправьте команду ещё раз.\n\n' + HELP_TEXT };
}

async function cmdExtract({ files }) {
  if (!files.length) return noFiles();
  const parts = [];
  const attachments = [];
  for (const f of files) {
    if (!canExtract(f.filename)) {
      parts.push(`■ ${f.filename}: формат не поддерживается (используйте CONVERT txt для DOC/PPTX)`);
      continue;
    }
    try {
      const text = await extractText(f.filename, f.content);
      const perFile = Math.floor(config.maxReplyTextChars / files.length);
      parts.push(`■ ${f.filename} (${text.length} символов)\n\n${clip(text, perFile) || '[текст не найден — возможно, это скан]'}`);
      attachments.push({ filename: `${baseName(f.filename)}.txt`, mimeType: 'text/plain; charset=UTF-8', content: Buffer.from(text, 'utf8') });
    } catch (err) {
      parts.push(`■ ${f.filename}: ошибка извлечения — ${err.message}`);
    }
  }
  return { text: parts.join('\n\n' + '─'.repeat(40) + '\n\n'), attachments };
}

async function cmdSummary({ files }) {
  if (!files.length) return noFiles();
  const parts = [];
  for (const f of files) {
    if (!canExtract(f.filename)) {
      parts.push(`■ ${f.filename}: формат не поддерживается`);
      continue;
    }
    try {
      const text = await extractText(f.filename, f.content);
      if (!text) {
        parts.push(`■ ${f.filename}: текст не найден (возможно, это скан без текстового слоя)`);
        continue;
      }
      const { text: summary, provider } = await summarize(f.filename, text);
      parts.push(`■ ${f.filename}  [${provider}]\n\n${summary}`);
    } catch (err) {
      parts.push(`■ ${f.filename}: ошибка — ${err.message}`);
    }
  }
  return { text: parts.join('\n\n') };
}

async function cmdOrganize({ drive, files, args, msg }) {
  if (!files.length) return noFiles();
  const date = new Date(Number(msg.internalDate) || Date.now()).toISOString().slice(0, 10);
  const sub = args.join(' ').trim() || date;
  const lines = [];
  for (const f of files) {
    const type = (extOf(f.filename).slice(1) || 'other').toUpperCase();
    const folderId = await ensureFolderPath(drive, [config.driveRootFolder, sub, type]);
    const uploaded = await uploadFile(drive, { name: f.filename, mimeType: f.mimeType, content: f.content, parentId: folderId });
    lines.push(`• ${f.filename} → ${config.driveRootFolder}/${sub}/${type}\n  ${uploaded.webViewLink}`);
  }
  return { text: `Сохранено в Google Drive (${files.length}):\n\n${lines.join('\n')}` };
}

async function cmdConvert({ drive, files, args }) {
  if (!files.length) return noFiles();
  const target = (args[0] || '').toLowerCase().replace(/^\./, '');
  if (!target) return { text: 'Укажите формат: например, тема «CONVERT pdf».\n\n' + HELP_TEXT };

  const lines = [];
  const attachments = [];
  for (const f of files) {
    const ext = extOf(f.filename);
    const outName = `${baseName(f.filename)}.${target}`;
    try {
      let content;
      if (driveCanConvert(ext, target)) {
        content = await convertViaDrive(drive, { filename: f.filename, ext, mimeType: f.mimeType, content: f.content, target });
      } else if (ext === '.docx' && target === 'html') {
        content = Buffer.from(await docxToHtml(f.content), 'utf8');
      } else if (target === 'txt' && canExtract(f.filename)) {
        content = Buffer.from(await extractText(f.filename, f.content), 'utf8');
      } else {
        lines.push(`• ${f.filename}: ${ext || '?'} → ${target} не поддерживается`);
        continue;
      }
      attachments.push({ filename: outName, mimeType: mimeFor(target), content });
      lines.push(`• ${f.filename} → ${outName}`);
    } catch (err) {
      lines.push(`• ${f.filename}: ошибка конвертации — ${err.message}`);
    }
  }
  return { text: `Результат конвертации:\n\n${lines.join('\n')}`, attachments };
}

const HANDLERS = {
  EXTRACT: cmdExtract,
  SUMMARY: cmdSummary,
  ORGANIZE: cmdOrganize,
  CONVERT: cmdConvert,
  HELP: async () => ({ text: HELP_TEXT }),
};

export async function runCommand(command, ctx) {
  return HANDLERS[command.name]({ ...ctx, args: command.args });
}
