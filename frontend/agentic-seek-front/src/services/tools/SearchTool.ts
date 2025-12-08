import axios from 'axios';

export class SearchTool {
    private apiKey: string;

    constructor(apiKey: string) {
        this.apiKey = apiKey;
    }

    async search(query: string): Promise<string> {
        // Using Serper.dev as it's a common, easy-to-use search API for agents
        // Or we could use Google Custom Search JSON API

        if (!this.apiKey) {
            return "Error: No Search API Key provided.";
        }

        try {
            // Attempt to use Serper (google wrapper)
            const response = await axios.post(
                'https://google.serper.dev/search',
                { q: query },
                {
                    headers: {
                        'X-API-KEY': this.apiKey,
                        'Content-Type': 'application/json'
                    }
                }
            );

            const data = response.data as any;
            if (data && data.organic) {
                const results = data.organic.map((r: any) =>
                    `Title: ${r.title}\nLink: ${r.link}\nSnippet: ${r.snippet}\n`
                ).join('\n');
                return results;
            }

            return "No results found.";

        } catch (error: any) {
             console.error("Search Error:", error);
             return `Search failed: ${error.message}`;
        }
    }
}
