import path from 'node:path';
import { PDFParse } from 'pdf-parse';
import mammoth from 'mammoth';
import ExcelJS from 'exceljs';

const TEXT_EXT = new Set(['.txt', '.md', '.csv', '.json', '.log', '.xml', '.yaml', '.yml']);

export function extOf(filename) {
  return path.extname(filename || '').toLowerCase();
}

export function canExtract(filename) {
  const ext = extOf(filename);
  return TEXT_EXT.has(ext) || ['.pdf', '.docx', '.xlsx', '.html', '.htm'].includes(ext);
}

function htmlToText(html) {
  return html
    .replace(/<(script|style)[\s\S]*?<\/\1>/gi, '')
    .replace(/<br\s*\/?>|<\/(p|div|h\d|li|tr)>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function cellText(value) {
  if (value == null) return '';
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  if (typeof value === 'object') {
    if ('result' in value) return cellText(value.result); // formula
    if ('text' in value) return String(value.text); // hyperlink
    if (Array.isArray(value.richText)) return value.richText.map((r) => r.text).join('');
  }
  return String(value);
}

async function xlsxToText(buffer) {
  const wb = new ExcelJS.Workbook();
  await wb.xlsx.load(buffer);
  const out = [];
  wb.eachSheet((sheet) => {
    out.push(`## ${sheet.name}`);
    sheet.eachRow({ includeEmpty: false }, (row) => {
      const cells = row.values.slice(1).map(cellText);
      out.push(cells.join('\t'));
    });
    out.push('');
  });
  return out.join('\n').trim();
}

/** Extracts plain text from a document buffer, picking the parser by file extension. */
export async function extractText(filename, buffer) {
  const ext = extOf(filename);
  if (ext === '.pdf') {
    const parser = new PDFParse({ data: new Uint8Array(buffer) });
    try {
      const result = await parser.getText();
      return result.text.trim();
    } finally {
      await parser.destroy();
    }
  }
  if (ext === '.docx') {
    const { value } = await mammoth.extractRawText({ buffer });
    return value.trim();
  }
  if (ext === '.xlsx') return xlsxToText(buffer);
  if (ext === '.html' || ext === '.htm') return htmlToText(buffer.toString('utf8'));
  if (TEXT_EXT.has(ext)) return buffer.toString('utf8').trim();
  throw new Error(`Формат ${ext || '(без расширения)'} не поддерживается для извлечения текста`);
}

export async function docxToHtml(buffer) {
  const { value } = await mammoth.convertToHtml({ buffer });
  return `<!doctype html><html><head><meta charset="utf-8"></head><body>${value}</body></html>`;
}
