import Anthropic from '@anthropic-ai/sdk';
import { config } from './config.js';

const SYSTEM = `Ты помощник, который делает краткие резюме документов.
Пиши на языке документа (если документ на английском — на английском).
Формат: 1–2 предложения о сути документа, затем 3–7 пунктов с ключевыми фактами, цифрами, датами и действиями.
Не добавляй сведений, которых нет в документе.`;

// Fallback when Claude is not configured: first sentences plus basic stats.
export function localSummary(text, maxSentences = 5) {
  const clean = text.replace(/\s+/g, ' ').trim();
  const sentences = clean.match(/[^.!?…]+[.!?…]+/g) || [clean];
  const words = clean ? clean.split(' ').length : 0;
  return [
    `Объём: ~${words} слов, ${clean.length} символов.`,
    '',
    'Начало документа:',
    ...sentences.slice(0, maxSentences).map((s) => `• ${s.trim()}`),
  ].join('\n');
}

let client;

/** Returns { text, provider }. Falls back to the local summary if the Claude call fails. */
export async function summarize(filename, text) {
  if (config.summaryProvider === 'local') return { text: localSummary(text), provider: 'local' };
  // ~3M characters is roughly the 1M-token context window; don't silently truncate.
  if (text.length > 3_000_000) {
    return { text: localSummary(text), provider: 'local (документ слишком большой для одного запроса к Claude)' };
  }

  try {
    client ??= new Anthropic();
    const stream = client.beta.messages.stream({
      model: config.claudeModel,
      max_tokens: 16000,
      output_config: { effort: 'low' },
      // On a policy decline the API retries on a server-chosen fallback model.
      betas: ['server-side-fallback-2026-07-01'],
      fallbacks: 'default',
      system: SYSTEM,
      messages: [
        {
          role: 'user',
          content: `<document name="${filename}">\n${text}\n</document>\n\nСделай резюме этого документа.`,
        },
      ],
    });
    const message = await stream.finalMessage();

    if (message.stop_reason === 'refusal') {
      return { text: localSummary(text), provider: 'local (Claude отказался обрабатывать документ)' };
    }
    const summary = message.content
      .filter((b) => b.type === 'text')
      .map((b) => b.text)
      .join('\n')
      .trim();
    return { text: summary || localSummary(text), provider: message.model };
  } catch (err) {
    console.warn(`[summary] Claude недоступен (${err.status ?? ''} ${err.message}); локальное резюме`);
    return { text: localSummary(text), provider: 'local' };
  }
}
