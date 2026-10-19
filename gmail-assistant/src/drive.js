import { Readable } from 'node:stream';
import { google } from 'googleapis';

const FOLDER_MIME = 'application/vnd.google-apps.folder';

export function driveClient(auth) {
  return google.drive({ version: 'v3', auth });
}

function escapeQuery(value) {
  return value.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
}

export async function findOrCreateFolder(drive, name, parentId) {
  const parent = parentId ? `'${parentId}' in parents` : `'root' in parents`;
  const q = `name = '${escapeQuery(name)}' and mimeType = '${FOLDER_MIME}' and ${parent} and trashed = false`;
  const { data } = await drive.files.list({ q, fields: 'files(id, name)', pageSize: 1 });
  if (data.files?.length) return data.files[0].id;
  const created = await drive.files.create({
    requestBody: { name, mimeType: FOLDER_MIME, parents: parentId ? [parentId] : undefined },
    fields: 'id',
  });
  return created.data.id;
}

/** Creates (or reuses) a nested folder path like ["AI Assistant", "2026-10-20", "PDF"]. */
export async function ensureFolderPath(drive, parts) {
  let parentId;
  for (const part of parts) parentId = await findOrCreateFolder(drive, part, parentId);
  return parentId;
}

export async function uploadFile(drive, { name, mimeType, content, parentId }) {
  const { data } = await drive.files.create({
    requestBody: { name, parents: parentId ? [parentId] : undefined },
    media: { mimeType, body: Readable.from(content) },
    fields: 'id, name, webViewLink',
  });
  return data;
}

// Office formats Drive can import into its native editors.
const IMPORT_AS = {
  '.docx': 'application/vnd.google-apps.document',
  '.doc': 'application/vnd.google-apps.document',
  '.odt': 'application/vnd.google-apps.document',
  '.rtf': 'application/vnd.google-apps.document',
  '.xlsx': 'application/vnd.google-apps.spreadsheet',
  '.xls': 'application/vnd.google-apps.spreadsheet',
  '.ods': 'application/vnd.google-apps.spreadsheet',
  '.pptx': 'application/vnd.google-apps.presentation',
  '.ppt': 'application/vnd.google-apps.presentation',
  '.odp': 'application/vnd.google-apps.presentation',
};

const EXPORT_MIME = {
  pdf: 'application/pdf',
  docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  txt: 'text/plain',
  html: 'text/html',
  csv: 'text/csv',
  odt: 'application/vnd.oasis.opendocument.text',
};

// What each native Google type can be exported to (subset of the Drive export matrix).
const ALLOWED_EXPORTS = {
  'application/vnd.google-apps.document': ['pdf', 'docx', 'txt', 'html', 'odt'],
  'application/vnd.google-apps.spreadsheet': ['pdf', 'xlsx', 'csv'],
  'application/vnd.google-apps.presentation': ['pdf', 'pptx', 'txt'],
};

export function driveCanConvert(ext, target) {
  const native = IMPORT_AS[ext];
  return Boolean(native && ALLOWED_EXPORTS[native].includes(target));
}

export function mimeFor(target) {
  return EXPORT_MIME[target] || 'application/octet-stream';
}

/**
 * Converts an Office file by importing it into Google Docs/Sheets/Slides and
 * exporting it in the target format. The temporary Drive copy is removed afterwards.
 */
export async function convertViaDrive(drive, { filename, ext, mimeType, content, target }) {
  const native = IMPORT_AS[ext];
  const { data: temp } = await drive.files.create({
    requestBody: { name: `tmp-convert-${filename}`, mimeType: native },
    media: { mimeType, body: Readable.from(content) },
    fields: 'id',
  });
  try {
    const res = await drive.files.export(
      { fileId: temp.id, mimeType: mimeFor(target) },
      { responseType: 'arraybuffer' },
    );
    return Buffer.from(res.data);
  } finally {
    await drive.files.delete({ fileId: temp.id }).catch(() => {});
  }
}
