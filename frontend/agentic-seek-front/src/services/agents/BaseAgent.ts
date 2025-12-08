// Abstract Base Agent Class
import { LLMProvider, ChatMessage } from '../LLMProvider';

export abstract class BaseAgent {
    protected name: string;
    protected provider: LLMProvider;
    protected messages: ChatMessage[] = [];
    protected systemPrompt: string = "";

    constructor(name: string, provider: LLMProvider) {
        this.name = name;
        this.provider = provider;
    }

    // Set the system prompt (can be loaded from file or string)
    setSystemPrompt(prompt: string) {
        this.systemPrompt = prompt;
        // Reset messages with system prompt
        this.messages = [{ role: 'system', content: prompt }];
    }

    async process(query: string): Promise<{ answer: string, reasoning: string }> {
        this.messages.push({ role: 'user', content: query });

        try {
            const response = await this.provider.chat(this.messages);

            // Basic parsing of reasoning if the model provides it in <think> tags or similar
            // For now, we assume the whole response is the answer, but DeepSeek R1 models use <think>

            let answer = response;
            let reasoning = "";

            if (response.includes('<think>')) {
                const parts = response.split('</think>');
                if (parts.length > 1) {
                    reasoning = parts[0].replace('<think>', '').trim();
                    answer = parts[1].trim();
                }
            }

            this.messages.push({ role: 'assistant', content: response });
            return { answer, reasoning };
        } catch (error: any) {
            console.error(`Error in agent ${this.name}:`, error);
            return { answer: "I encountered an error processing your request.", reasoning: error.message || String(error) };
        }
    }

    getHistory() {
        return this.messages;
    }
}
