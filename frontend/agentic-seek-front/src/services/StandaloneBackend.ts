import { agentManager } from './AgentManager';
import { browserState } from './BrowserState';

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
        // Expose Browser Snapshot
        if (url.includes('browser_snapshot')) {
             return { data: browserState.getSnapshot() };
        }
        // Legacy screenshot support (can be removed or kept for compatibility)
        if (url.includes('screenshots')) {
             throw new Error("Use browser_snapshot for standalone");
        }
        return { data: {} };
    }
};

export default StandaloneBackend;
