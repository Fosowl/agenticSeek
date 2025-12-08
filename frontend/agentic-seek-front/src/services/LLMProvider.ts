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
            const response = await axios.post(url, { contents });

            const data = response.data as any;
            if (data && data.candidates && data.candidates.length > 0) {
                 const text = data.candidates[0].content.parts[0].text;
                 if (verbose) console.log("Gemini Response:", text);
                 return text;
            } else {
                console.error("Gemini Empty Response:", response.data);
                throw new Error("Empty response from Gemini");
            }

        } catch (error) {
            console.error("Gemini API Error:", error);
            throw error;
        }
    }
}
