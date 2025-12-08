import { BaseAgent } from './BaseAgent';
import { LLMProvider } from '../LLMProvider';

// Simplistic Casual Agent
const CASUAL_PROMPT = `You are a helpful AI assistant named AgenticSeek.
You are running natively on an Android device.
Answer the user's questions to the best of your ability.
Be concise and helpful.`;

export class CasualAgent extends BaseAgent {
    constructor(provider: LLMProvider) {
        super("CasualAgent", provider);
        this.setSystemPrompt(CASUAL_PROMPT);
    }
}
