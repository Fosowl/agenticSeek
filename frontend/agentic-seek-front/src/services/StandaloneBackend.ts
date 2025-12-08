import { agentManager } from './AgentManager';

// Simulates the axios calls but routes them to local AgentManager
const StandaloneBackend = {
    post: async (url: string, body: any) => {
        if (url.endsWith('/query')) {
            console.log("Standalone Query:", body.query);
            const response = await agentManager.processQuery(body.query);
            return { data: response };
        }
        return { data: {} };
    },
    get: async (url: string) => {
        if (url.endsWith('/health')) {
            return { data: { status: "healthy", version: "standalone-0.1" } };
        }
        if (url.endsWith('/latest_answer')) {
            // In standalone mode, we don't poll, but the frontend still calls this.
            // We can return a default empty state or last state.
            // Since processQuery awaits the result, the UI will update then.
            // So we can return empty here to avoid double-updates.
             return { data: { answer: "" } };
        }
        if (url.endsWith('stop')) {
            return { data: { status: "stopped" } };
        }
        // Mock screenshot
        if (url.includes('screenshots')) {
             // Return a blob of a placeholder
             // For now we can throw error or return empty, App.js handles error
             throw new Error("No screenshot in standalone");
        }
        return { data: {} };
    }
};

export default StandaloneBackend;
