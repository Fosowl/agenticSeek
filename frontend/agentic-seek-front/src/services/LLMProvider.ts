import axios from 'axios';

// Interface for LLM provider
export interface LLMConfig {
    provider: string; // "gemini" | "openai"
    apiKey: string;
    model: string;
}

export interface ChatMessage {
    role: 'system' | 'user' | 'assistant';
    content: string;
}

export class LLMProvider {
    private config: LLMConfig;

    constructor(config: LLMConfig) {
        this.config = config;
    }

    async chat(messages: ChatMessage[], verbose: boolean = false): Promise<string> {
        if (this.config.provider === 'gemini') {
            return this.geminiChat(messages, verbose);
        } else {
            throw new Error(`Provider ${this.config.provider} not supported in this version.`);
        }
    }

    private async geminiChat(messages: ChatMessage[], verbose: boolean): Promise<string> {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${this.config.model}:generateContent?key=${this.config.apiKey}`;

        // Convert messages to Gemini format
        // Gemini expects: { parts: [{ text: "..." }], role: "user" | "model" }
        // System prompt is handled differently in newer Gemini API, but we can prepend it to first user message or use system_instruction if model supports it.
        // For simplicity, we prepend system prompt to first user message for now.

        let systemPrompt = "";
        const contents = [];

        for (const msg of messages) {
            if (msg.role === 'system') {
                systemPrompt += msg.content + "\n";
            } else {
                let content = msg.content;
                if (systemPrompt) {
                    content = systemPrompt + "\n" + content;
                    systemPrompt = ""; // Clear it so we don't add it again
                }

                contents.push({
                    role: msg.role === 'assistant' ? 'model' : 'user',
                    parts: [{ text: content }]
                });
            }
        }

        // If system prompt is left over (e.g. no user message yet?), prepend a dummy user message?
        // AgenticSeek usually starts with system then user.

        try {
            return await this.makeRequestWithRetry(url, { contents }, verbose);
        } catch (error) {
            console.error("Gemini API Error:", error);
            throw error;
        }
    }

    private async makeRequestWithRetry(url: string, data: any, verbose: boolean, retries = 3, delay = 1000): Promise<string> {
        try {
            const response = await axios.post(url, data);

            const responseData = response.data as any;
            if (responseData && responseData.candidates && responseData.candidates.length > 0) {
                 const text = responseData.candidates[0].content.parts[0].text;
                 if (verbose) console.log("Gemini Response:", text);
                 return text;
            } else {
                console.error("Gemini Empty Response:", response.data);
                throw new Error("Empty response from Gemini");
            }
        } catch (error: any) {
            if (retries > 0 && error.response && error.response.status === 429) {
                console.warn(`Gemini API 429 Rate Limit. Retrying in ${delay}ms... (Retries left: ${retries})`);
                await new Promise(resolve => setTimeout(resolve, delay));
                // Exponential backoff
                return this.makeRequestWithRetry(url, data, verbose, retries - 1, delay * 2);
            }
            throw error;
        }
    }
}
