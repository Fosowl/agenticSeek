import { BaseAgent } from './BaseAgent';
import { LLMProvider } from '../LLMProvider';
import { SearchTool } from '../tools/SearchTool';
import { ReadPageTool } from '../tools/ReadPageTool';

const BROWSER_SYSTEM_PROMPT = `You are a Browser Agent.
You can search the web and read website content.
Your goal is to answer the user's question using the information you find.

When asked to search, use the Search tool.
When asked to read a page, use the Read Page tool.

If you have enough information, answer the user.
`;

export class BrowserAgent extends BaseAgent {
    private searchTool: SearchTool;
    private readPageTool: ReadPageTool;

    constructor(provider: LLMProvider, searchApiKey: string) {
        super("BrowserAgent", provider);
        this.setSystemPrompt(BROWSER_SYSTEM_PROMPT);
        this.searchTool = new SearchTool(searchApiKey);
        this.readPageTool = new ReadPageTool();
    }

    async process(query: string): Promise<{ answer: string, reasoning: string }> {
        // Simple ReAct loop or Tool Use simulation
        // For simplicity, we'll do a one-shot "Check if search is needed"

        // 1. Ask LLM what to do
        this.messages.push({ role: 'user', content: query + "\n\nDecide your next step:\n1. If you need to search, output SEARCH: <query>\n2. If you need to read a page from previous results, output READ: <url>\n3. If you have the answer, output ANSWER: <answer>\n" });

        // Loop max 3 steps for safety
        for (let i = 0; i < 3; i++) {
            const res = await this.provider.chat(this.messages);
            this.messages.push({ role: 'assistant', content: res });

            if (res.includes("SEARCH:")) {
                const searchQuery = res.split("SEARCH:")[1].split("\n")[0].trim();
                const searchResults = await this.searchTool.search(searchQuery);
                this.messages.push({ role: 'user', content: "Search Results:\n" + searchResults });
            } else if (res.includes("READ:")) {
                 const url = res.split("READ:")[1].split("\n")[0].trim();
                 const pageContent = await this.readPageTool.read(url);
                 this.messages.push({ role: 'user', content: "Page Content:\n" + pageContent });
            } else {
                // Assume answer
                let answer = res;
                if (res.includes("ANSWER:")) {
                    answer = res.split("ANSWER:")[1].trim();
                }
                return { answer: answer, reasoning: "Processed query with tools." };
            }
        }

        return { answer: "I reached the step limit without a final answer.", reasoning: "Step limit reached" };
    }
}
