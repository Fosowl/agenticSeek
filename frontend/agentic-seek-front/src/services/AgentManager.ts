import { CasualAgent } from './agents/CasualAgent';
import { BrowserAgent } from './agents/BrowserAgent';
import { LLMProvider } from './LLMProvider';

export interface BackendResponse {
    done: string;
    answer: string;
    reasoning: string;
    agent_name: string;
    success: string;
    blocks: any;
    status: string;
    uid: string;
}

export class AgentManager {
    private provider: LLMProvider;
    private currentAgent: CasualAgent | BrowserAgent;
    private apiKey: string;
    private searchApiKey: string;

    constructor() {
        this.apiKey = localStorage.getItem('GEMINI_API_KEY') || "";
        this.searchApiKey = localStorage.getItem('SEARCH_API_KEY') || "";
        this.provider = new LLMProvider({
            provider: 'gemini',
            apiKey: this.apiKey,
            model: "gemini-1.5-flash"
        });
        this.currentAgent = new CasualAgent(this.provider);
    }

    setApiKey(key: string) {
        this.apiKey = key;
        localStorage.setItem('GEMINI_API_KEY', key);
        this.reinit();
    }

    setSearchApiKey(key: string) {
        this.searchApiKey = key;
        localStorage.setItem('SEARCH_API_KEY', key);
        this.reinit();
    }

    private reinit() {
        this.provider = new LLMProvider({
            provider: 'gemini',
            apiKey: this.apiKey,
            model: "gemini-1.5-flash"
        });
        // Logic to switch agents? For now default to Casual or Browser if keywords present
        this.currentAgent = new CasualAgent(this.provider);
    }

    hasApiKey(): boolean {
        return !!this.apiKey;
    }

    async processQuery(query: string): Promise<BackendResponse> {
        if (!this.apiKey) {
             return {
                done: "true",
                answer: "Please set your Gemini API Key in the settings.",
                reasoning: "No API Key provided.",
                agent_name: "System",
                success: "false",
                blocks: {},
                status: "Error",
                uid: Date.now().toString()
            };
        }

        // Simple Router
        if (query.toLowerCase().includes("search") || query.toLowerCase().includes("find") || query.toLowerCase().includes("web")) {
            this.currentAgent = new BrowserAgent(this.provider, this.searchApiKey);
        } else {
             this.currentAgent = new CasualAgent(this.provider);
        }

        const result = await this.currentAgent.process(query);

        return {
            done: "true",
            answer: result.answer,
            reasoning: result.reasoning,
            agent_name: (this.currentAgent as any).name || "Agent",
            success: "true",
            blocks: {},
            status: "Ready",
            uid: Date.now().toString()
        };
    }
}

export const agentManager = new AgentManager();
