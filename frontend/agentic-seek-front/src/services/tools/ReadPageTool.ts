import { CapacitorHttp } from '@capacitor/core';
import { browserState } from '../BrowserState';

export class ReadPageTool {

    constructor() {}

    async read(url: string): Promise<string> {
        try {
            // Use CapacitorHttp to bypass CORS on Android/iOS
            const options = {
                url: url,
            };

            // In a real browser environment (during dev), CapacitorHttp might fall back to fetch
            // and hit CORS. In Android, it works natively.
            const response = await CapacitorHttp.get(options);

            if (response.status !== 200) {
                return `Error: Failed to load page. Status: ${response.status}`;
            }

            const html = response.data;

            // Process HTML for display (Inject Base Tag)
            let processedHtml = html;
            const baseTag = `<base href="${url}" target="_blank">`;

            // Robust injection logic
            if (!/<base\s/i.test(processedHtml)) {
                if (/<head\b/i.test(processedHtml)) {
                    // Inject after <head ...>
                    processedHtml = processedHtml.replace(/(<head\b[^>]*>)/i, `$1${baseTag}`);
                } else if (/<html\b/i.test(processedHtml)) {
                    // Inject after <html ...> if head missing
                    processedHtml = processedHtml.replace(/(<html\b[^>]*>)/i, `$1<head>${baseTag}</head>`);
                } else {
                    // Prepend to content if even html missing (rare but possible partials)
                    processedHtml = `<head>${baseTag}</head>${processedHtml}`;
                }
            }

            // Update Browser State for UI
            browserState.setPage(url, processedHtml);

            // Basic HTML text extraction using DOMParser (browser native)
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Remove scripts and styles
            const scripts = doc.querySelectorAll('script, style, noscript');
            scripts.forEach(script => script.remove());

            // Get text content
            const text = doc.body.textContent || "";

            // Clean up whitespace
            const cleanText = text.replace(/\s+/g, ' ').trim();

            // Truncate if too long (LLM context limit)
            return cleanText.substring(0, 10000);

        } catch (error: any) {
             console.error("Read Page Error:", error);
             return `Read failed: ${error.message}`;
        }
    }
}
