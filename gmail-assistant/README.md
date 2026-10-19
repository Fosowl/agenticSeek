# Gmail Assistant

Ассистент, который принимает команды по почте: вы отправляете письмо с командой в теме и документами во вложении, он отвечает в той же ветке.

| Команда (тема письма) | Что делает |
|---|---|
| `EXTRACT` | Извлекает текст из вложений; ответ — текст в письме + `.txt` файлы |
| `SUMMARY` | Краткое резюме каждого вложения (Claude, или локально без API) |
| `ORGANIZE [папка]` | Кладёт вложения в Google Drive: `AI Assistant/<папка или дата>/<PDF\|DOCX\|…>` и присылает ссылки |
| `CONVERT <формат>` | Конвертирует вложения: `pdf`, `docx`, `xlsx`, `pptx`, `txt`, `html`, `csv` |
| `HELP` | Справка |

Поддерживаемые форматы для EXTRACT/SUMMARY: PDF, DOCX, XLSX, HTML, TXT, CSV, JSON, MD.
CONVERT через Google Drive умеет DOC/DOCX/ODT/RTF → pdf/docx/txt/html/odt, XLS/XLSX/ODS → pdf/xlsx/csv, PPT/PPTX/ODP → pdf/pptx/txt.

## Установка

Нужен Node.js 20+.

```bash
cd gmail-assistant
npm install
cp .env.example .env
```

В `.env` обязательно укажите `ALLOWED_SENDERS` — свой адрес.

### Google Cloud (один раз, ~5 минут)

1. Откройте https://console.cloud.google.com/ и создайте проект.
2. **APIs & Services → Library**: включите **Gmail API** и **Google Drive API**.
3. **APIs & Services → OAuth consent screen**: тип *External*, заполните название и email. В **Test users** добавьте свой Gmail.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**, тип **Desktop app**.
5. Скачайте JSON и сохраните его как `gmail-assistant/credentials.json`.

Авторизация (откроется браузер):

```bash
npm run auth
```

Токен сохранится в `token.json`. `credentials.json` и `token.json` уже в `.gitignore` — не коммитьте их.

> Пока приложение в статусе *Testing*, Google выдаёт refresh-токен на 7 дней. Через неделю запустите `npm run auth` снова, либо переведите приложение в *Production* на экране OAuth consent.

### Claude для SUMMARY (необязательно)

Задайте `ANTHROPIC_API_KEY` в `.env`. Без ключа (или с `SUMMARY_PROVIDER=local`) резюме строится локально: объём и первые предложения документа. Документы при этом никуда не отправляются.

## Запуск

```bash
npm start
```

`npm run once` — один проход по почте без цикла (удобно для проверки и cron).

### Проверка

Отправьте себе письмо:

- Тема: `SUMMARY`
- Вложение: любой PDF или DOCX

В течение минуты придёт ответ в той же ветке, а исходное письмо получит ярлык `AI-Assistant/Processed`.

## Безопасность

- Команды принимаются **только** от адресов из `ALLOWED_SENDERS`. Поле From легко подделать, поэтому письмо дополнительно должно быть либо отправлено с этого же аккаунта (ярлык SENT), либо пройти проверку DMARC (`dmarc=pass` в заголовке Authentication-Results от Gmail). Остальные письма помечаются ярлыком и игнорируются.
- Доступ к Drive ограничен scope `drive.file`: ассистент видит только файлы, которые создал сам.
- Ответы помечаются заголовком `X-AI-Assistant`, поэтому ассистент не обрабатывает собственные письма. Темы вида `Re: …` командами не считаются.
- При `SUMMARY_PROVIDER=claude` текст документов отправляется в Anthropic API.

## Работа в фоне

```bash
npx pm2 start src/index.js --name gmail-assistant
npx pm2 save
```

## Структура

```
src/
  index.js      цикл опроса, обработка письма, ответ
  commands.js   разбор темы и команды EXTRACT/SUMMARY/ORGANIZE/CONVERT/HELP
  gmail.js      поиск писем, вложения, проверка отправителя, MIME-ответ
  drive.js      папки, загрузка, конвертация через Google Docs/Sheets/Slides
  extract.js    извлечение текста из PDF/DOCX/XLSX/HTML/текста
  summarize.js  резюме через Claude с локальным запасным вариантом
  auth.js       OAuth 2.0 и token.json
  config.js     настройки из .env
test/           тесты без доступа к сети (npm test)
```

## Что дальше

Telegram, Slack, Discord и Web API можно добавить как отдельные входы, которые вызывают `runCommand()` из `src/commands.js`: логика команд от Gmail не зависит.
